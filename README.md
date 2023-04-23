# UVcageTex

UVcageTexはblenderで作成したUVマップの座標を元にテクスチャ変形させるデスクトップアプリケーションです。
シーンとして、UVを移動した場合に設定済のテクスチャを追従させること想定しています。
テクスチャを複数のマップで分けている場合も考慮し、複数の画像に対して変形できるようにしています。
<br>
###### 左：変形前　右：変形後
![image](https://user-images.githubusercontent.com/124477558/233796348-56da3b45-1df9-4a9d-a5df-73674d46fc4a.png)
<br>
###### 上：変形前　下：変形後
![image](https://user-images.githubusercontent.com/124477558/233796684-4ac76c70-2b73-4482-a39f-0812fa0f9fc8.png)
<br>

### Usage

|GUI|Instructions|
|:----|:----|
|![image](https://user-images.githubusercontent.com/124477558/233797106-be389e97-cc99-4f02-bfb8-b3aec03c9d14.png)|<b># Select folder with Textture JPG or PNG</b><br>変形したいテクスチャ（jpg or png）のディレクトリを指定します。画像は複数可。<br><br><b># Before UV SVG & After UV SVG</b><br>変更前(Before)と変更後(After)UVを設定します。<br><br>* データ形式：SVG</b><br>SVGはBlenderのUVエディタからエクスポートしたSVGが対象。<br>他ツールで編集・保存したSVGは動作対象外。<br><br>* ポリゴン<br>三角ポリゴン数を一致させて、UV座標のみ動かしたSVGを設定してください。<br>追加・削除・分割等が行われたものは動作しません。<br><br><b># START</b><br>上記の操作後に変形処理が実行できます。<br>処理時間はCPU性能・三角ポリゴン数・テクスチャ解像度およびファイル数に依存します。|
<br>

### Download
* https://github.com/Yuuzen401/UVcageTex/releases/download/v1.0.0/UVcageTex.zip

### 動作環境
Win10でビルド・開発しています。他環境については未確認です。
<br>

### 課題

###### 処理速度
* 残念ながら、速いとは言えません。まずハイポリには適していません。
モンキーモデル(▲：968)で2048*2048のテクスチャをi7-12700でテストした結果、42秒を計測。
内部的にはポリゴン単位で変形と合成を繰り返しているために時間を要しています。
高速化にあたりCythonを試しましたが、処理部分はnumpyとopencvに委ねているので大した変化は見られませんでした。ポリゴン単位の処理ではなく包括的なアプローチをしないと解決できないでしょう。

###### 今後
* 元々はblenderにアドオンとして搭載するつもりで開発していました。何かしらの連携機能は加えるつもりです。
<br>

### その他
UIに使用したアイコンは以下のgitからお借りしています。
ありがとう。素晴らしいアイコンです。
ライセンス規約に従い、UIにコピーライトを表示しています。
https://github.com/Shrinks99/blender-icons