# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import Canvas, PhotoImage, Button, filedialog, messagebox
import numpy as np
import cv2
from PIL import Image
import platform
import os
from typing import List
import typing
from helper import validate_xml, parse_points, get_files

Mat: typing.TypeAlias = 'np.ndarray[int, np.dtype[np.generic]]'

NO_FILE_SELECTED_NO_FOLDER = "No Folder selected"
NO_FILE_SELECTED_NO_FILE = "No file selected"

def get_path(root, title, filetypes):
    # Windowsの場合withdrawの状態だとダイアログも
    # 非表示になるため、rootウィンドウを表示する
    if platform.system == "Windows":
        root.deiconify()
    # macOS用にダイアログ作成前後でupdate()を呼ぶ
    root.update()
    # ダイアログを前面に
    root.lift()
    root.focus_force()
    path = filedialog.askopenfilename(
        # initialdir="/",
        title=title,
        filetypes=filetypes
    )
    root.update()
    if platform.system == "Windows":
        # 再度非表示化（Windowsのみ）
        root.withdraw()
    return path

class UVcageTex(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.input_tex_path = NO_FILE_SELECTED_NO_FOLDER
        self.before_uv_svg_path = NO_FILE_SELECTED_NO_FILE
        self.after_uv_svg_path = NO_FILE_SELECTED_NO_FILE

    def get_path_text(self):
        if self.input_tex_path == "" or self.input_tex_path is None :
            self.input_tex_path = NO_FILE_SELECTED_NO_FOLDER
        if self.before_uv_svg_path == "" or self.before_uv_svg_path is None :
            self.before_uv_svg_path = NO_FILE_SELECTED_NO_FILE
        if self.after_uv_svg_path == "" or self.after_uv_svg_path is None :
            self.after_uv_svg_path = NO_FILE_SELECTED_NO_FILE
        text = f"input : {self.input_tex_path}\n\n\
Before UV : {self.before_uv_svg_path}\n\n\
After UV : {self.after_uv_svg_path}"
        return text

    def is_enable(self):
        if self.input_tex_path == NO_FILE_SELECTED_NO_FOLDER or \
            self.before_uv_svg_path == NO_FILE_SELECTED_NO_FILE or \
            self.after_uv_svg_path == NO_FILE_SELECTED_NO_FILE :
            return False
        else :
            return True

    def toggle_execute(self):
        if self.is_enable() :
            image_ui_start_img = ui_start_img,
            # image_ui_start_gpu_img = ui_start_gpu_img,
            activebackground = "#4772B3"
            highlightcolor = "#545454"
            bg = "#545454"
        else :
            image_ui_start_img = ui_start_img_disabled,
            # image_ui_start_gpu_img = ui_start__gpu_img_disabled,
            activebackground = "#484848"
            highlightcolor = "#484848"
            bg = "#484848"
        
        ui_start_button.config(image=image_ui_start_img, activebackground=activebackground, highlightcolor=highlightcolor, bg=bg)
        #ui_start_gpu_button.config(image=image_ui_start_gpu_img, activebackground=activebackground, highlightcolor=highlightcolor, bg=bg)

    # 各ファイルの選択後に呼び出される関数を更新
    def select_input_tex_file(self):
        self.input_tex_path = filedialog.askdirectory()
        self.toggle_execute()
        canvas.itemconfig(text_item, text=self.get_path_text())

    def select_before_uv_svg_file(self):
        path = get_path(self.master, "Select Before UV SVG File", [("SVG files", "*.svg")])
        self.before_uv_svg_path = path
        self.toggle_execute()
        if path == "" or path is None :
            self.before_uv_svg_polygons = ""
            canvas.itemconfig(text_item, text=self.get_path_text())
            return 
        if not validate_xml(path) :
            messagebox.showinfo("svg format error", "Select the svg you exported from blender\nSVGのフォーマットが正しくありません。blenderのUVエディタからエクスポートしたsvgを使用してください")
            return
        
        self.before_uv_svg_polygons = len(parse_points(path , 1, 1))
        canvas.itemconfig(text_item, text=self.get_path_text())

    def select_after_uv_svg_file(self):
        path = get_path(self.master, "Select After UV SVG File", [("SVG files", "*.svg")])
        self.after_uv_svg_path = path
        self.toggle_execute()
        if path == "" or path is None :
            self.after_uv_svg_polygons = ""
            canvas.itemconfig(text_item, text=self.get_path_text())
            return 
        if not validate_xml(path) :
            messagebox.showinfo("svg format error", "Select the svg you exported from blender\nSVGのフォーマットが正しくありません。blenderのUVエディタからエクスポートしたsvgを使用してください")
            return
        
        self.after_uv_svg_polygons = len(parse_points(path , 1, 1))
        canvas.itemconfig(text_item, text=self.get_path_text())

    def execute_cpu(self):
        return self.execute(False)

    def execute_gpu(self):
        return self.execute(True)

    def execute(self, use_gpu):
        if not self.is_enable() :
            messagebox.showinfo("message", "Required selection not made\n必要な選択が行われていません")
            return

        if not os.path.exists(self.input_tex_path):
            messagebox.showinfo("message", "Selected folder does not exist\n選択したフォルダーが存在しません")
            return
        if not os.path.exists(self.input_tex_path):
            messagebox.showinfo("message", "Selected folder does not exist\n選択したフォルダーが存在しません")
            return

        entries = get_files(self.input_tex_path)
        if 0 == len(entries) :
            messagebox.showinfo("message", "JPG/PNG does not exist in the selected folder\n選択したフォルダーにJPG/PNGが存在しません")
            return

        if use_gpu :
            if cv2.cuda.getCudaEnabledDeviceCount() < 1 :
                messagebox.showinfo("message", "GPU not supported or used\nGPUがサポート対象外または使用されていません")
                return
            title, message = self.transform_image(
                self.input_tex_path,
                self.before_uv_svg_path,
                self.after_uv_svg_path,
                use_gpu,
            )
        else :
            title, message = self.transform_image(
                self.input_tex_path,
                self.before_uv_svg_path,
                self.after_uv_svg_path,
                use_gpu,
            )
        messagebox.showinfo(title, message)

    def transform_image(self, input_tex_dir: str, before_uv_svg_path: str, after_uv_svg_path: str, use_gpu: bool) -> tuple:
        output_tex_dir = os.path.join(input_tex_dir, "output")
        if not os.path.exists(output_tex_dir):
            os.mkdir(output_tex_dir)

        # フォルダ内の画像ファイルのパスを取得
        entries = get_files(input_tex_dir)

        # 進行状況バーの作成
        root = tk.Tk()
        root.title("Progress")
        progress = Progressbar(root, orient=tk.HORIZONTAL, mode="determinate", length=300)
        progress.pack(pady=10)

        # SVGのポリゴンをパース
        b = parse_points(before_uv_svg_path, 1, 1)
        a = parse_points(after_uv_svg_path, 1, 1)

        # ポリゴン数が等しくない場合は終了する
        if len(b) != len(a) :
            message = f"選択したSVGの三角形ポリゴン数が合わないため、画像の変換は行われませんでした。\n\
Before : {len(b)}\n\
After : {len(a)}"
            return ("message", message)

        task = len(b)*len(entries)
        count = 0
        for entry in entries:
            
            # 画像を読み込む
            img = cv2.imread(entry)
            height, width = img.shape[:2]

            file_name = os.path.basename(entry)
            output_tex_path = os.path.join(output_tex_dir, "new_" + os.path.splitext(file_name)[0] + ".png")

            # スケールを考慮してSVGポリゴンをパース
            src = parse_points(before_uv_svg_path, width, height)
            dst = parse_points(after_uv_svg_path, width, height)

            # import time
            # start = time.time()
            if use_gpu :
                base, ret_count = UVcageTex.apply_affine_transform_gpu(src, dst, img, progress, task, count)
            else :
                base, ret_count = UVcageTex.apply_affine_transform(src, dst, img, progress, task, count)
            # print(time.time() - start, use_gpu)
            count = count + ret_count

            # 画像を保存する
            base.save(output_tex_path)

        progress.stop()
        progress_window = progress.winfo_toplevel()
        progress_window.withdraw()
        progress.destroy()
        return ("Transformation Complete", f"Output saved to {output_tex_dir}")

    @staticmethod
    def apply_affine_transform(src_list: np.ndarray, dst_list: np.ndarray, img: Mat, progress: Progressbar, task: int, count: int) -> tuple:
        base = Image.new("RGBA", (img.shape[1], img.shape[0]), color=(0, 0, 0, 0))

        for src, dst in zip(src_list, dst_list):
            count = count + 1

            # アフィン変換する
            M = cv2.getAffineTransform(src, dst)
            result = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_AREA,borderMode=cv2.BORDER_REPLICATE)
            result = cv2.cvtColor(result, cv2.COLOR_RGBA2BGRA)

            # マスクを作成する
            mask = np.zeros(result.shape[:2], dtype=np.uint8)
            points = np.array([dst[0], dst[1], dst[2]], dtype=np.int32)
            cv2.fillPoly(mask, [points], (255, 255, 255, 255))

            # マスクされていない領域を黒色で塗りつぶす
            mask = np.expand_dims(mask, axis=2)
            result = np.where(mask == 0, np.zeros_like(result), result)

            # 画像を重ねる（合成はPILで実行。CV2で合成すると画像の境目にノイズが発生する）
            clip = Image.fromarray(result)
            base.paste(clip, (0, 0), clip)

            # 進行状況バーを更新する
            progress["value"] = int((count / task) * 100)
            progress.update()
        return (base, count)

    # TODO::GPU処理を実装したが、CPU処理のほうが高速。いい方法がないだろうか。
    @staticmethod
    def apply_affine_transform_gpu(src_list: np.ndarray, dst_list: np.ndarray, img: Mat, progress: Progressbar, task: int, count: int) -> tuple:
        base = Image.new("RGBA", (img.shape[1], img.shape[0]), color=(0, 0, 0, 0))

        # GPUを使用するために、CUDAを有効にする
        cv2.cuda.setDevice(cv2.cuda.getDevice())
        stream = cv2.cuda_Stream()

        for src, dst in zip(src_list, dst_list):
            count = count + 1

            # アフィン変換する
            M = cv2.getAffineTransform(src, dst)
            img_gpu = cv2.cuda_GpuMat(img)
            result = cv2.cuda.warpAffine(img_gpu, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE, stream=stream)
            result = cv2.cuda_GpuMat(result)
            result = result.download()
            result = cv2.cvtColor(result, cv2.COLOR_RGBA2BGRA)

            # マスクを作成する
            mask = np.zeros(result.shape[:2], dtype=np.uint8)
            points = np.array([dst[0], dst[1], dst[2]], dtype=np.int32)
            cv2.fillPoly(mask, [points], (255, 255, 255, 255))

            # マスクされていない領域を黒色で塗りつぶす
            mask = np.expand_dims(mask, axis=2)
            result = np.where(mask == 0, np.zeros_like(result), result)

            # 画像を重ねる（合成はPILで実行。CV2で合成すると画像の境目にノイズが発生する）
            clip = Image.fromarray(result)
            base.paste(clip, (0, 0), clip)

            # 進行状況バーを更新する
            progress["value"] = int((count / task) * 100)
            progress.update()
        return (base, count)

def on_closing():
    window.destroy()
    window.quit()

if __name__ == "__main__":
    window = tk.Tk()
    uv_cage_tex = UVcageTex(window)
    window.geometry("400x558")
    window.title("UVcageTex")    
    window.configure(bg = "#3d3d3d")
    window.protocol("WM_DELETE_WINDOW", on_closing)
    canvas = Canvas(
        window,
        bg = "#3d3d3d",
        width = 400,
        height = 558,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge")
    canvas.place(x = 0, y = 0)
    ui_logo_img = PhotoImage(
        data="iVBORw0KGgoAAAANSUhEUgAAAOkAAABDCAYAAAB5sCJrAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAABLmSURBVHgB7Z17cBTVnsd/0zMTEgzQWlpXHntpCsqFC/cyESzUKkmnEN1CJIlrFWqVZmKpuKtVGSmVx25VJn9Y4AMycLUUpTYTLB8UrBkeIq6PTGSlUF6T4gZBCel4uYSrXDISQkgyM31/v57TY6czmfRAwElyPlXNzHSfc/p009/z+53fOX0CwOFwOBwOh8PhcDgcDofD4XA4nMGHDQYI2VMjZoPDBVeZ3b77g8DhDCMcMEBk2x0uVYVauAwiZ49YS2jPhvn/Wa0I2dev+3TtIh9wOMOAARPpldDV9InltELWaMnx+3mV9y7dDlyogxtVVUWbzRYGTkoEGGTEus5Dd9MuUKOd5eRiA2cwU6PGqcWtErci3CTg9GDQiZRAgUK09YToBJCAMyhBMbrxQ2Y/6dODWw1uTXjsMBOtDJzBKdIENvsY4Aw6mLUsT5GEApAkWrKwJNoqsrIwTBncIuUMVkigksW0lM4Ncde4dTgKNiMCR5zhxWOPPQaTJ0+GWbNmadvYsWOtZqUYhJs2FKqCn0Hc1mHwKQRDGC5SzjXnyJEjFQ0NDXU7duzIx58yClWSZVkT7C233GK1GAl+FWwAhVoMQxQuUs41JxQKKfjhZxsIgpB/6NAhcmHl8vJyV35+PrS0tFgW7DvvvDOko/xcpJzfnP3799fhRx2L+FbRvu+//x6WLFkC999/f0qX+PTp07BhwwY/DGF44IiTEZgjviRMtKqwadOmIApVqaiogIMHD/bK99577ym4vxqGMMPGktLsFoiPw9Vh/8WbTnrcZkI8aFGczgwZFoUsw60C8wWBk4peEd9x48bB+vXrg2hFK8jK7ty5swT3yU8++aQmYtwHmzdv9sIQZzhZUhKZjNvEdNPjg+Bi30sgPSrRHdMeKk7fMDfXbd5PruyiRYu0RhH7rP4DBw4U/Pjjj5O8Xq+frOuzzz475K0owfukFnj//ff9CxYs8I4aNYoG2NdZycNmy0gKgg/XkB4iuBJSTWwgEWJ/tcf9ZkGnUvoejUYlGAYMqEgjZ/8CXU27IF1G3vYiXA4xdHeuBdh6r/v88889xcXFEonPouuqWd233noriA8Wn0TeN0knNrz99tvQ1NRUkCojE+yQh1tSC5DImpub/RCfqkYPVTBVemYd3DgOqI0JggVYH5j6sDR2SPlJ2ArEB+uVJOll/ChkaUWWnsYLq1OUTw2Hy1A+WfhqKp+VV8J+B/vJF4B4316BKyCVm4vDKt5kIjTUs6K/8+tpMV1pkmN0PeErvYZrARepRTCKuO2uu+7yYMBCtmBNNfftyy+/9Ftp7dnDREMPUltbmzb8gK61Pk7oweM+PN9zydLSeCJ9UlrMQ2+RePFYgfHhYwEsyiMa8+C10H4vHqeGhNK7wdAAGc9FeUg8rF6Uj4Tt7atRsEhSNxe9D+oiVJjukcTqIrNddK0k1F6vKxqCfjL7/Zwx4Ie/qbGtHKBruOpwkVoEH5rg1q1bgyRSiLfkwWTpdCtKwwVff/11v/1XJqAaEgAbZgizaW4iRjJdFHRauHAhCZX2Vxw7dqwEB/+lNWvW6GkVTBsmy/DII4+IS5cupfPTw1yQonwtDwpOfuihh+Cpp54isYRM9SJLU2vIp7B8Wr1effVVCcXqx3S/4P4ApAlrTCTzfvI+PvnkE0+Se6Q1Mvo+bGRErH8leyfVa0yPIheffvpp2bBLoutj4iVRlxj20zXUZ/LUQi7SNMB+acWDDz5I09iKzK2zAZn+wWhkEIMeVv7jKQKsBUlOnTpF4q7TD7hcLgkjmeW4z42NhLZv2bJlCqYP4bk9xrQE7UPhVKKoZd2d66d8Ed3KMrSSXprpY6pXTap6PfPMMzVvvPGGC89XhecKpjk0JUEfVnTLli0Uxd1mSKs1MvpvvdF4+OGHgaYSUjn0Qio1YHqaDRs2hAsLC40TIPLZXF9aOcRlLOuFF16AH374ATIZPpkhDciaYjAjCPEWvayPZOVWZ8GwPplEA/IUJGEzbxKQq4ziKN2+fXspCkWzyhTEwnrkmdOy+vm6urr87CeN7cr9lB8mt/Ljjz8uNU4UYMJIWa+zZ88WYHBHs/gQ7xunQ1KBmvvwTMyV+m+90bjhhhtKmUA1GhsbZVP9wufOnVMMu9y4HQaDQOl6H330UeXo0aN5FhvT3wwu0jT58MMPA9Sfg3hfscecUaPoLI7fUZAIxowZ403Vd6UxQj1CbIwU0/npQTZu48ePNz5wM62Ujw+pnzU+lvNRPdrb259jP2WwiN4dMO8nAZIVNZ2vR+R3+fLlYbTg3lWrVvUQOVpWxVweNmbG++AylkORY3SHgyjkPDxfxg+PcZGmCbba1R999BEJRY96GtGsaGtrqxesIdE/GzdurIc0oP4cvQyNX1txazJuc+bMMQZStEZkwoQJ/ZZ/++23B8z1wr6qX03Bm2++eTkLzyW1onv27FFMVpSE5Tam2bRpkzhv3jw/mASXLIK+e/fuoHkfNa7kKlPkmCZGDJahsWHTJ8VgArWe9NVlMYtE/2CgpsdO+o9FkfoeeOABmtxAbqHmhhonL2Dgo87KCdB6waRJk+Dbb7+loIyVLHQeEmHZBx98AMFgUIvUGtHnvBI///wz3HTTTbBgwQKxv3JRyInver7nn38emNeQko6ODrACs6JF5v3UsCWJhJelKovcVRIoehkJa888Geqvh9atW3e9MT1dB1rh8PHjxz0o0GpTvWSWLyNFO2xEaggmSKq1Veo0l+/EiROK+QD1C7/55hvP3XffbRyOMU5eUMACnZ2dejpqOIL9pWfudRmJc+3atTQsE3A6nYoxzZ133klRXe1NEnS7wx6PFijNt1B+IqJaX18fxmuDqVOnelEI/eWD7u7uZrCGDIYIrQ41bNhQmbsHPfqP1CjR8I8+RIWNEwWrvOiqk5dQxuov4RbE+0SNZA+LTXmnTZtW+u6772oeg8HtLmN1osZjG2QgAybSaFTIaNeBLOBXX32lLF68WAI26b2vtEwMHmrh8eEIJSsLH6oAPshuiEcXFUhz8gJRWVmpYONBX/udIMHQHvCcnJwAWoPnkiWYP39+4juN7eL1erBhIvd4W1/DDObhEBRmPbrN8MQTT9C8Y8vXY4G+xkWTNWwJkZ48eTJYV1fn0xtXdHkVDKblQVxkJC6j8GXoo4+8YsWKEtyo3PwkaWh/Rop0wPqk10GXYhenhG32EZCp0Bxc5h562YB2L5hAqa8lUT8Jo39JXdeamppqFhGVgUUgUaD+UBpT1ch6kIWgMvC8lX3UR2Zr+3jIZSdLggIS+0grgUEIFI1euXKlwlxWfQU+l6lsGt4oJ+usg0MSAb/fH2b1qlGTLLPJgla+vu5jsvRoASXz/mQNm/l8t956KwW3ZLyeIvz0rV69mhob8hbcwARKDarZ9d+5c6fmEhsgQdP9kfUddG8oDb23mqkMmEgDvuKwTcipcE5aALYRmbmIH7mp2C9R2H8mPbBN7MEtZxv9x1MAxkX/ca+99pq/r+CCPrmB/SwiFywQCPghDUjQ5LYyoXoM9XHjVoYbNRY0oUBcsmTJGHLZDeIh0RUxoekzjQ5jwyEZz9HQ0FCMQw1h1qCQoA7rgR9WdhG9XI1DPJobiIExzVPAIE0Fe8Dpwa5V4wuAlbG6VbL7VIZuf76Va83Ly6M+YYiEYyRJRBfuuOOOHuKaPHmyzOquDQ0Z09J1Ud950aJFCoo3UQ6dh96WweElb7J+tS7OoqKiMAWS9CGuTGRA+6Sf+hb67vXsBHvOjWWxjrMSrY+bSTDBFeDDUvv4449LtLYOuoIJS6D3d/SAhHlqmhma3FBaWirTlDyMJoaSjV32B7mtKFQ6r2fhwoVUpx71IQFv3rxZweGCal08+L0SI68urHtikF8PpOAYoj4rSoPGAF0uVx4GzaqwnjJZJWPfjmYSCYLgxgaALGxRJBIJs3r58GMMHvfiuahe7j7uk6UhDKo71qMAhePD/CU0GYHqnKx7sG/fPgXr4b1w4YJ36dKlvcqiRpYsMOWnSSO4y4ffyZ2XsU61NIZKAqUx5mg0KmKgz1NSUiIa7xObeeXD86zL9CivtZDiZTD/he2WWtgrobs7Wh9ECw5pQjNm7Ha75vaMHj1ays3N1fajVdGm5LGAhCXBzZ49WxskJwtzJe82onjcKBYKPsn6TBlWn14PEqXF/eV63fFhJuFogRSafANxy9erPrfddpsLH9p8PI8Yi8XCeA8SDQvzItxoVWQUZZ0hTz6z0uZ6pXWfjOA9q8S+rgeHqoI49lmQIp0HBVc5d+5cTZjUMKAo4fz58xQN91PAznx+zFMuimIRNqB5+j60suX33Xefl1x6dOWDl1vv34qrJtLBAk2NGzlypOaf792712qU8qqCEdqJ9NlfffS6X7x48Ze+rIHev0v1tgdLQ66vhA/zpL761VbrZQUSE36EjFMAk0FTMLFRKWTBuRA2WHX9WT66L8Y09NvhcJRhOQGMA6Q1Js3hXHVYX7KJTYCQkhyX2XH1lVdeaQIOh3NtwaBRFQ7gGycKUeColm2aONF9VDFIpqLVSnd5GM41YNi7u0Md6n+jq1eDQSNtPVv23ql2jIYtqJ+3a9euMPZpvealSjiZARfpMIGCRmg06W0ViuJqkU7qp2IgKYRBpGq+xAuHw+FwOBwOh8PhcDgcMzxwxBkQ2pbNkG2CWiXEIDDy5Yakb+hcWDGdxmGV3FUNBXAVaFs5PWBTYeZ1Qky2vfRdRkxMGQj4QmScBBdXziizqWr4Uodz2/W+y4r2SqpNTfWCuQRw9RY0R4GOAet/QXzQwEXK0WhfPqM88Fe759wlCG384creqzy/4o9FdjU6U6CpiDFnXc7LyacZqh6X2DEyUqLGYqI57YXlf3CjmzdRULOqVXukkNKoUdiW++rRULL80ZiadLofWXjBFtPmkVNZevl6HalMwSnkx7pjdcayMwkuUg50LHNJUVtEjqkQUi7aaG2uMAmgLburyKbGlFEvHwvqaduWTZVzO7NDbVmd8uhXvguYy1IFoUhQY27VZoMo/rYJ3Uqrx5Vntsx0zotCd62qgnTmkgA356haWtxfoAnJZitBmytHhYgH6B1fWl7GAd7zL04rpvNS/nZ75LB+TLDbaOA3DIY/PYLudS3WSG7pECDXCZDr6PZ2rJjuzlnVUG1XY4VYRzeVqf25Egd+N609nCnwhcg4sO9crLClw+aaMkoV5d/FNAGdcUaadv7NWfntuayqduxLotDiEyAEe02LM1L7xd+zkr6kfuYiiE/sywb5sxzY+qODnFspK7ur13pFMXt3OR17/XgWLN4zQnloTza0RWxSVOiuMqbbqthFOuZvdGq/7She+tTSoUBpP53Lc2AEgGH1RrLE+CHTcSr/yX0jwmc6tIbD16O+uI/ylnydDZkKFykHnj/kbP5Hp6rsPi2EyuudIRLAhu+dsPY7p//FQ85gVaPTKDTxP77JEl9qcAaSldXcLign2+2uAwcO2Gr/btcEgTZSNqdT2fIo94zrDtfdc0lZM+uSkuvQrKDLmK72J7vvXGyEFAoLXi2fzaYLUaJ//Ccd9N6vrT5sl0+0/RoHtYFNc3HvHRfRyn/t1kvh3LjORfW/pk3U021sdCqUt/F8NCOXTiG4u8uhF6ADf5w/vXCmeMnv3XasDu6Z7m2LqIlV9dbPmqGAISDTfD5WEAodUpKVNefGqKK/Dvb6rC568D3h7t7pTrUL4oSRMfio2SmeufSriDsiPdP553T4bC8dav5i2dTqKNi95nL2zItU5xzQXm6v+508Q19qFf7RBXADGtdPTzvEUKsgG/Mcbc+Gz+b+on1f/C+dntU7Dmf0u6VcpJxefNbigIo/dbvWfAyaSF03qtKOvzoTx/tZx0luXzm9CmIq9itVN9lGFEqvSPHnp+2Ke0pMck/phiOt9oDTBuKE66LyjlOOUrDA/6Ir/e+/j0AM+7Xty//gRwsro51NuLvrj48Ie//UCf82PgLjR9o1qz8xNyb/X4vTu/Gzvc0wd7qWbuqYWMbPWeYi5fTi7UZnIKqqHgy8yPhT3KI4pD8fd7it5P3/n+0wJTfmvjkH+4URm9aX3NIs9HKN/6dRqL4QdcoPotDmj43Q2kUQOmcH0QGWRPPn404/NgBezC9hwMhLfUu0yOC6PqYdr/vJXv3foSzPs//anSj/RJsA43MiMNjgIuVoyF+MTHxvaYtUrPqLU1zdkEVvztDbMr6DB+OuLwVpklHwRSLwEqAVCcfmgNTSAWFBELwHD+5P5FVZ9JX+dIYgzBa3NNvLRjnjrjSKOhiJRBTjebKysuLl14mAxxLno/WnXofZ4uvHnZ6bs1XAc+l/9U2mPPv37w3FZs0q3vPTiEpD+SF9WVO6XnZtwOEMS/SlVqxAy5vQBpdJf+e60vI5HA6Hw+FwOBwOh8PhcDgcDofD4XA4HA6Hw+FwOBwOh8PhcAaIfwLLyTfs7CrL6QAAAABJRU5ErkJggg=="
    )
    canvas.create_image(
        206.5, 46.5,
        image=ui_logo_img)
    ui_tex_img = PhotoImage(
        data = "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"
    )
    ui_tex_button = Button(
        image = ui_tex_img,
        activebackground="#4772B3",
        highlightcolor="#545454",
        bg="#545454",
        borderwidth = 0,
        highlightthickness = 0,
        command = uv_cage_tex.select_input_tex_file,
        relief = "flat")
    ui_tex_button.place(
        x = 24, y = 83,
        width = 352,
        height = 35)
    ui_after_img = PhotoImage(
        data = "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"
    )
    ui_after_button = Button(
        image = ui_after_img,
        activebackground="#4772B3",
        highlightcolor="#545454",
        bg="#545454",
        borderwidth = 0,
        highlightthickness = 0,
        command = uv_cage_tex.select_before_uv_svg_file,
        relief = "flat")
    ui_after_button.place(
        x = 24, y = 131,
        width = 172,
        height = 35)
    ui_before_img = PhotoImage(
        data = "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"
    )
    ui_before_button = Button(
        image = ui_before_img,
        activebackground="#4772B3",
        highlightcolor="#545454",
        bg="#545454",
        borderwidth = 0,
        highlightthickness = 0,
        command = uv_cage_tex.select_after_uv_svg_file,
        relief = "flat")
    ui_before_button.place(
        x = 204, y = 131,
        width = 172,
        height = 35)

    canvas.create_rectangle(
        24, 179, 24+352, 167+255,
        fill = "#2d2d2d",
        outline = "")

    text_item = canvas.create_text(
        32, 184,
        fill = "#ffffff",
        anchor="nw",
        justify="left",
        text=uv_cage_tex.get_path_text(),
        width=338
    )

    ui_start_img = PhotoImage(
        data="iVBORw0KGgoAAAANSUhEUgAAAWAAAAAjCAYAAACq2tA6AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJdSURBVHgB7doxixpRFIbhCWwrWGsR8w8EFcQmxsZKiKCNjQbEStx0lvoPtraSNBYWLsFWcFtF0dZqAqKWo6KNCDf3mJnsrBiWrI0s7wOHGebeO+XH4cwYBgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG6DUsqr60GXqWui6/vZesC4wrXnAeDdkuBttVoqlUqpXC6n+v2+fqRqrnVlXOHa8wDwLtndrwqHww+xWOxjJBIJJpPJx3a73bfXa+oPuQZdZ+q6mrryrncFdH3VVZC1f50HAGjBYNC7XC6VHagB55kO4nu5r1arp3ZYrsViMW6H76ljrlQqZq/Xs5xuWV9l3ep0Ola9XleXzhsAgGfpdNrsdrtqu91KVvbdXa0O4s/yUK4SzFKJRMKUjlmelcvlRwlk2SsBPBqNTt10KBTKXzpvAACe6WAM6MBs6rJKpZIzA2466+cz3Pl8fm+PH8z1em26A1gC/Pz9zIAB4AJ7pPB3NiudqsyAZZTg2qNc9/HFYnEaP+hO2MpkMhMCGADeQHe7QQlb969iMg/WXe6LAJagtu8Lg8HAckYK9uz41QB2zgMAbNFoNNBoNJT9Ie7UzcocVzpbZ4+s2yGdz2azhdls5uydyOz4tQB2nzeAG/DBAG6E/mhWk87W7/dLR+tdrVZPx+Px23Q6/eWsezye+n6/LxwOh593d3d9n88X2O12681m86S3xMfj8Se9L67vazrAv5y/3zk/HA5/GACAl+Q/YKlLa+d/MMi+//mrgT8gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA37jfnR+y4TLIJcQAAAABJRU5ErkJggg=="
    )
    ui_start_img_disabled = PhotoImage(
        data="iVBORw0KGgoAAAANSUhEUgAAAWAAAAAjCAYAAACq2tA6AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAMHSURBVHgB7dq7SiNRHMfxkxADWrgTC7FLgi+QWpCMoIWdb7DJE2xSeWkm23jBYmefYLWwN7WIs514S0RRENQYUETQnRW8xdv+jzigMuxNIbPs9wOHyZzLTCN//vxGpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+M+FFBAQuVzOaGxstORnnwxXxuTIyIjtrff39yfGxsYq6i+99jzw1iIKCAgpvqW9vb1EtVpVDQ0Nqr29PTUwMPBudHT0o14Ph8O76hVNw2vPA2+NP0YEgmVZRq1W+zYzM2NHo1H7+vo6JkXYSiaTxtTUVJcUYisUChXu7+8Lt7e3xfHx8fJjx5yT+bjMO9ItT+pn6U5X7lNScA0Z6eHh4azfeQXUWVgBAVAsFtXFxYXq6en53tnZGVpcXCyfn59nt7a2pvX62tqa6V1LpZKhC/Zjx2ytrKyYh4eHti6yj49LRCKRL/v7+5/W19czfucVEABEEAiEcrnsNjc3V6TjtVpbW63BwUFHpiekq/2s14+OjgpycfRVuuNVXbClACv5bUtnOy2dba6trS0jex7iiuPjY2Nzc9OW+bLfeQUEAAUYgXF6etolHevDR7iWlhYzHo+bQ0NDpo4QpCP+2t3drfTV25/P520pwikpshM3NzfPnhWLxZylpaW8d+93Hqg3IggEgs5zJX4wlpeXszJiruuaGxsburPt89svOa8pa7aOHxzHMRYWFlwF/GMowAiEs7MzndvO6Q9o+l53qul0elVy4Gf7dKHWV4kdErLmStSQkew42dHRUfyd93jngSCgACMQ5OOYu729bVxdXe1K/luSsXtycmJJNlzx9si6ampq0uvv5+fnVTQaNSRWsHt7e+cODg6sX73j6XkFBAAZMAJBCmpFctyCFMmMFEn9b2TG5eWlI3NZb8/Ozk6hWq0W7u7uVK1Wm5YzHyQDTshHNVfGhOTHpt43Ozvr+46n5wEAPiROiOvht5ZKpYyXe1/O/cyf7AUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoA5+AEDUgOleqZ2mAAAAAElFTkSuQmCC"
    )
    ui_start_button = Button(
        borderwidth = 0,
        highlightthickness = 0,
        command = uv_cage_tex.execute_cpu,
        relief = "flat")
    ui_start_button.place(
        x = 24, y = 436,
        width = 352,
        height = 35)

    # ui_start_gpu_img = PhotoImage(
    #     data="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"
    # )
    # ui_start__gpu_img_disabled = PhotoImage(
    #     data="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"
    # )
    # ui_start_gpu_button = Button(
    #     borderwidth = 0,
    #     highlightthickness = 0,
    #     command = uv_cage_tex.execute_gpu,
    #     relief = "flat")

    # ui_start_gpu_button.place(
    #     x = 24, y = 484,
    #     width = 352,
    #     height = 35)
    uv_cage_tex.toggle_execute()

    canvas.create_text(
        395, 549,
        text = "Shrinks99 / blender-icons / CC BY-SA 4.0",
        fill = "#ffffff",
        anchor="e",
    )

    icon = tk.PhotoImage(
        data="iVBORw0KGgoAAAANSUhEUgAAAEAAAABBCAYAAABhNaJ7AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAR1SURBVHgB5ZtLSFRRGMe/OzlQJjTVIu0BkdoiQkbIhaUyEeVjY220hRvbBC00CgIxsiAUhMCEFm3UoJW2KCI0WhTowkhwchP4oBY1KqRZ+BhfM53/qSs2qXPu3HPuveP9weFO01l0f993vvudcyet+MbLKNnI/IdmUsgMG8FoNPp8ZWXlRX9//5fYCR7a3vjYCGia1uL1ej8XFRXdjZ2w3QX8A8uEBiZhMBAI+PTvXCUAMAn+SCTyVv+z6wQASCgoKGjAZ1cKAKwuXMdScK0Aho89GWqVCjiwN5WcDMuCQAopIvPgHnp0s5Dmwis09u0nDY1O0dDYFI2FftHcwjI5BL8yAXeunOLX3TtTKCdzPx86YyEImWZCvtP7T2k0OztLNuHTVHSCVcXHqerCceH5wWCQBgcH165WIj0DDuxLNXTzwO/38wEmJia4hL6+Pn5VnR3SM+DJ7XOs+O0iWUBEb28vHypkSBVgNPWNokKGNAFpu7z07H4xWQVkdHd3cxlmkJoBSH1e8bP+VH3UA9XoNaOnpyehAqqpPA9AL5CTuY/yT6ZzKaqBjPb2di4Cn0XQrDoQQT9w+q8IXHezJaOSsrIyoTqhrBGKBR3hm4GvfDygj3yJoGiub5BkgdogWiRt2wxN/lhYqxHj4+O8mOEqAywDUSzLgFjwuNT7hYyMDB6x2tpa3hAVFhbykQiIvuj6B5odh6KXio7R1fIT/32Pf3hNTQ2/pqencxnV1dVckCgVFRWGBFi+BHirXLxxs4Sbbm1t5VfcBB5tlZWVXAoiGw+j0QeWZ4BIq4zl0NjYyJud9cTLCqPRB5bWAEReZJ+QlrbxFlnPCgyIKC0t5QMkEn1gmQAju8S2tja+Nd4K/D0GKj5kxJu/GZYJaL6WLzQPj8KOjg4SRc+KRLGkCKLqi26R8Si0EuUCtqr6sSD1E1nHZlAuAOse+4B4GE19WSgVcD7vCBuHheZanfo6ygQYSf3Ozk7LU18nRdX7+ct1dUKFb3J6nl4N76fUvFtkB0oyAB2b3qDE4+nrYb4ztAslAtDGijAyMsLPB+xEugBEPisrS2hufX092Y10AdioiJBo7y4bqQIQfax/EYyc2qhEqoBkiz6QJkA0+uj4nBJ9IE1AMkYfSBFgJPpmtq4qkCIgWaMPTAvIzc0Vij6OuJwWfWBaQElJidA8vPhwWvSBKQFGen4nVf71mBKQzGtfx5SA7OxsoXlOjT4wJQC7vngvNJ0cfWBKwOjoKD/K2kqCyCstOzH9FEB0N5OA/X6iLyysQkojpEvADa+nq6uLnI60vYAuQf/VlhPb3o2Quh1Gt4dTHqz7ZIg+UPJusKmpib/hTQY80aianwfY+AtwQ2AJzJCL8ayurjr7OaUYCHinahkkA56lpaWHTIJrl4GHdWozy8vLLW7NAt4HDAwM3FtcXAy6UcJaI8Sy4Gw4HA6yK7mJHfoH1sqGQ6HQY5zysJoQiEQi/HtN0/hQhffQGbKTDe/M7/cf9Xg85WxcxP+zZQJ8tE35DQsqKAnnIxtjAAAAAElFTkSuQmCC"
    )
    window.iconphoto(True, icon)    
    window.resizable(False, False)
    window.mainloop()
    window.quit()