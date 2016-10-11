# umakaviewer
http://v.umaka.dbcls.jp/ にアップロードするためのファイルを作成するコマンドラインツールです。

# インストール
`$ pip install umakaviewer`  
のあと  
`$ umakaparser`  
を実行し、ヘルプが表示されれば正常にインストールできています。

# 用意するもの
1. [Sparql Builder Metadata ver.2015](http://www.sparqlbuilder.org/doc/sbm_2015sep/)に従うデータ
2. 上記のクロール先のSparql Endpointのオントロジー

ファイル形式は現在Turtle形式にのみ対応しています。

# アップロードするファイルを作成するまでの手順

`$ umakaparser build_index {2のTurtleファイル} --dist {出力先のパス}`  

を実行すると、出力先のパスにディレクトリが作成されます。  

`$ umakaparser build {1のTurtleファイル} --assets {build_indexで作成されたディレクトリ} --dist {出力先のパス}`  

これによって作成されたJSONを、http://v.umaka.dbcls.jp/ でアップロードすることで、グラフとして閲覧することができます。  
各コマンドの使い方は`--help`オプションを与えることで見ることができます。

## トラブルシューティング

多くのOSであらかじめインストールされているsetuptoolsでは一部の依存ライブラリのインストールがうまくいかないようです。  
インストールに失敗する場合は  

`$ pip install -U setuptools`

を実行したのち再度試してみてください。
