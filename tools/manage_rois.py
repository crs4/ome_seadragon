import abc
from itertools import product
import json
from csv import DictReader
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import defopt

import ezomero
from ezomero.rois import Polygon
from omero.gateway import BlitzGateway

SLIDE = str
REVIEW = str


class ShapeReader(abc.ABC):
    def shapes(self) -> Iterable[Polygon]:
        ...


class ROIImporter(abc.ABC):
    @abc.abstractmethod
    def get_shape_reader(self, path: Path) -> ShapeReader:

        ...

    def __init__(self, root_dir: Path, ome_connection: BlitzGateway):
        self._root_dir = root_dir
        self._ome_connection = ome_connection

    def import_rois(
        self,
        slides: Optional[Dict[SLIDE, List[REVIEW]]] = None,
        stroke_color: Tuple[int, ...] = (0, 0, 0, 0),
        stroke_width: int = 20,
    ):
        slides = slides or {d.name: [] for d in self._root_dir.iterdir()}
        for slide, reviews in slides.items():
            self._import_slide(slide, reviews, stroke_color, stroke_width)

    def _import_slide(self, slide, reviews, stroke_color, stroke_width):
        ome_slide = self._ome_connection.getObject("Image", attributes={"name": slide})
        reviews = reviews or (self._root_dir / slide).iterdir()
        for review in reviews:
            self._import_review(ome_slide, review, stroke_color, stroke_width)

    def _import_review(self, ome_slide, review, stroke_color, stroke_width):
        shape_reader = self.get_shape_reader(review)
        for shape in shape_reader.shapes():
            ezomero.post_roi(
                self._ome_connection,
                ome_slide.id,
                shapes=[
                    shape,
                ],
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                name=shape.label,
            )


class CSVShapeReader(ShapeReader):
    def __init__(self, csv_path: Path, label_column: str):
        self._csv_path = csv_path
        self._label_column = label_column

    def shapes(self) -> Iterable[Polygon]:
        csv_basedir = self._csv_path.parent
        with self._csv_path.open() as f:
            reader = DictReader(f)
            for row in reader:
                shape_filename = row["file_name"]
                with (csv_basedir / shape_filename).open() as f:
                    yield Polygon(points=json.load(f), label=row[self._label_column])


class CoreImporter(ROIImporter):
    def get_shape_reader(self, path) -> ShapeReader:
        return CSVShapeReader(path / "cores.csv", "core_label")


class FocusRegionImporter(ROIImporter):
    def get_shape_reader(self, path) -> ShapeReader:
        return CSVShapeReader(path / "focus_regions.csv", "region_label")


def _get_ome_connection(
    ome_host: str,
    ome_port: str,
    ome_user: str,
    ome_password: str,
) -> BlitzGateway:

    ome_connection = ezomero.connect(
        host=ome_host,
        port=ome_port,
        user=ome_user,
        password=ome_password,
        group="",
        secure=True,
    )
    if ome_connection is None:
        raise RuntimeError("Impossible to connect to omero")
    return ome_connection


def import_(
    path: str,
    *,
    ome_host: str,
    ome_port: str,
    ome_user: str,
    ome_password: str,
    slides: Optional[List[str]] = None,
    stroke_color: Tuple[int, ...] = (0, 0, 0, 0),
    stroke_width: int = 20,
):
    ome_connection = _get_ome_connection(
        ome_host=ome_host,
        ome_port=ome_port,
        ome_user=ome_user,
        ome_password=ome_password,
    )

    try:
        core_importer = CoreImporter(Path(path) / "cores", ome_connection)
        focus_region_importer = FocusRegionImporter(
            Path(path) / "focus_regions", ome_connection
        )

        slides_dct = {s: [] for s in slides} if slides is not None else None
        core_importer.import_rois(
            slides=slides_dct, stroke_color=stroke_color, stroke_width=stroke_width
        )
        focus_region_importer.import_rois(
            slides=slides_dct, stroke_color=stroke_color, stroke_width=stroke_width
        )
        ome_connection.close()
    finally:
        ome_connection.close()


def delete(
    *,
    project: Optional[int] = None,
    slides: Optional[List[int]] = None,
    ome_host: str,
    ome_port: str,
    ome_user: str,
    ome_password: str,
):
    if project and slides:
        raise RuntimeError("project and slides are mutually exclusive")

    if project is None and slides is None:
        raise RuntimeError("Specify project or slides")

    ome_connection = _get_ome_connection(
        ome_host=ome_host,
        ome_port=ome_port,
        ome_user=ome_user,
        ome_password=ome_password,
    )

    try:
        if project:
            slides = ezomero.get_image_ids(ome_connection, project=project)

        slides = slides or []
        for slide in slides:
            for roi in ezomero.get_roi_ids(ome_connection, slide):
                ome_connection.deleteObjects(
                    "Shape", ezomero.get_shape_ids(ome_connection, roi)
                )
                ome_connection.deleteObjects(
                    "ROI",
                    [roi],
                )
    finally:
        ome_connection.close()


if __name__ == "__main__":
    defopt.run({"import": import_, "delete": delete})
