# TwiFollow（IkedaYuki0220/TwiFollow.git）
 
TwitterAPIを利用して、好きなハッシュタグやキーワードを元に
 
ユーザを自動でフォローするツールです。
 
# デモ
 
キーワード「cooking」を指定した場合

そのキーワードを最近呟いたユーザを自動でフォローします。

<img src="https://user-images.githubusercontent.com/62292461/76877033-24dcad00-68b6-11ea-8a04-cc056f9dc62a.jpg" width="250">

フォローが完了するとTwitterのDMに通知が届きます。
 
# ファイルの説明

* follow.py
```bash
実行ファイル
```
   
* app_ini.csv
```bash
twitterAPIキーの設定ファイル
```

* follow_history.csv
```bash
過去にフォローしたユーザを記録するファイル
```

* follow_ini.csv
```bash
フォロー条件の設定ファイル

【設定値の説明】
follow_num
　　フォローする人数

follow_keyword
　　フォローする対象を探すためのキーワード
　　例）#おうちごはん

setting_1
　　 TRUE  ⇒ 過去にフォローした履歴があるユーザはフォローしない
     FALSE ⇒ 過去にフォローした履歴があるユーザもフォローする

setting_2
　　 TRUE  ⇒ 相互にフォローしていないユーザのみフォローする
     FALSE ⇒ 相手が自分に片思いでもフォローする
```
 
