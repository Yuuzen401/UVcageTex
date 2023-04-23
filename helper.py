import xml.etree.ElementTree as ET
import numpy as np
import os

def validate_xml(path: str) -> bool:
    try:
        # XMLをパースして、ルート要素を取得する
        tree = ET.parse(path)
        root = tree.getroot()
    
        # ルート要素を検証する
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            return False
        if "width" not in root.attrib or "height" not in root.attrib:
            return False
    
        # 子要素を検証する
        for child in root:
            if child.tag != "{http://www.w3.org/2000/svg}desc" and child.tag != "{http://www.w3.org/2000/svg}polygon":
                return False
            if child.tag == "{http://www.w3.org/2000/svg}polygon":
                if "stroke" not in child.attrib or "stroke-width" not in child.attrib or "fill" not in child.attrib or "points" not in child.attrib:
                    return False
    
        polygons = parse_points(path , 1, 1)
        if len(polygons) == 0 :
            return False
    except Exception:
        return False
    return True

def polygon_to_triangles(polygon):
    triangles = []
    for i in range(1, len(polygon) - 1):
        triangle = [polygon[0], polygon[i], polygon[i+1]]
        triangles.append(triangle)
    return triangles

def parse_points(file_path: str, width: int, height: int) -> np.ndarray:
    """
    SVG ファイルからポリゴンを読み込み、ポリゴンの頂点データを計算して返す。
    """
    # SVG ファイルを解析して ElementTree オブジェクトを取得
    tree = ET.parse(file_path)
    root = tree.getroot()
    # SVG の幅・高さを取得
    svg_width = root.attrib["width"]
    svg_height = root.attrib["height"]
    # 解像度に対する SVG の比率を計算
    ratio_x = int(width) / int(svg_width)
    ratio_y = int(height) / int(svg_height)
    polygons = []
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    # 各ポリゴンに対して以下の処理を行う
    for i, polygon in enumerate(root.findall("svg:polygon", namespace)):
        # 座標文字列を数値リストに変換
        points_str = polygon.get("points")
        points = [list(map(float, point.split(","))) for point in points_str.split()]
        # ポリゴンの重心を計算
        x_coords, y_coords = zip(*points)
        cx = sum(x_coords) / len(x_coords)
        cy = sum(y_coords) / len(y_coords)
        # 重心を中心とした座標系に変換し、解像度に合わせて拡大縮小する
        expanded_points = [[
            ((x - cx)  * 1 + cx) * ratio_x,
            ((y - cy) * 1 + cy) * ratio_y
        ] for x, y in points]
        # ポリゴンの頂点数が 3 以上の場合、三角形に分割する
        if len(expanded_points) > 3:
            expanded_points = polygon_to_triangles(expanded_points)
            for triangle in expanded_points:
                polygons.append(triangle)
        else:
            polygons.append(expanded_points)
    # ポリゴンの頂点データを返す
    return np.array(polygons, dtype=np.float32)

def get_files(input_tex_dir):
    # ディレクトリ内のフォルダエントリを取得
    entries = []
    with os.scandir(input_tex_dir) as files:
        for file in files:
            # 画像ファイルである場合のみ処理する
            if not file.is_file() or file.name.lower().endswith((".png", ".jpg", ".jpeg")) is False:
                continue
            else :
                entries.append(file.path)
    return entries