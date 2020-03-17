# TwiFollow（IkedaYuki0220/TwiFollow.git）
 
TwitterAPIを利用して、好きなハッシュタグやキーワードを元に
 
ユーザを自動でフォローするツール。
 
# DEMO
 
ツールの流れ

> ```flow
st=>start: Start :>http://www.google.com[blank]
op1=>operation: twitterのDMに実行開始を通知
io=>inputoutput: 設定ファイル読み込み
app_ini.csv
follow_ini.csv
op1=>operation: 
sub1=>subroutine: My Subroutine
cond=>condition: Yes 
or No?
e=>end

st(right)->op1(right)->io(right)->sub1(right)->cond
cond(yes)->e
cond(no)->op1
> ```
 
# Features
 
"hoge"のセールスポイントや差別化などを説明する
 
# Requirement
 
"hoge"を動かすのに必要なライブラリなどを列挙する
 
* huga 3.5.2
* hogehuga 1.0.2
 
# Installation
 
Requirementで列挙したライブラリなどのインストール方法を説明する
 
```bash
pip install huga_package
```
 
# Usage
 
DEMOの実行方法など、"hoge"の基本的な使い方を説明する
 
```bash
git clone https://github.com/hoge/~
cd examples
python demo.py
```
 
# Note
 
注意点などがあれば書く
 
# Author
 
作成情報を列挙する
 
* 作成者
* 所属
* E-mail
 
# License
ライセンスを明示する
 
"hoge" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
 
社内向けなら社外秘であることを明示してる
 
"hoge" is Confidential.