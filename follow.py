# coding: utf-8
import tweepy
from time import sleep
import schedule,time,datetime
import sys
import json
import csv
import pprint
import pandas
import os
from requests_oauthlib import OAuth1Session
from collections import OrderedDict

# グローバル変数を定義
api = None # twitterAPIインスタンス
csvWriter = None # ユーザ情報を書き込むCSVのインスタンス
follow_count = 0 # フォローした人数をカウント
error_count = 0 # エラーをカウント ⇒ APIを制限を回避

def main():
    global api
    global csvWriter
    global follow_count
    global error_count

    # 環境パスを取得
    base = os.path.dirname(os.path.abspath(__file__))

    # API設定ファイル
    app_ini = os.path.normpath(os.path.join(base, 'app_ini.csv'))

	# ツール条件設定ファイル
    follow_ini = os.path.normpath(os.path.join(base, 'follow_ini.csv'))

	# ユーザ情報書き込み用ファイル
    follow_history = os.path.normpath(os.path.join(base, 'follow_history.csv'))

    # app_ini.csvからAPIキーを取得
    with open(app_ini, "r") as f:
        reader = csv.DictReader(f)
        reader_list = [row for row in reader] #{ 式 for 変数 in オブジェクト｝
        api_key = reader_list[0]['API_key']
        api_secret_key = reader_list[0]['API_secret_key']
        access_token = reader_list[0]['Access_token']
        access_token_secret = reader_list[0]['Access_token_secret']

    # follow_ini.csvからツールの設定を取得
    with open(follow_ini, "r") as f:
        reader = csv.DictReader(f)
        reader_list = [row for row in reader]
        follow_num = reader_list[0]['follow_num'] # フォローする数をCSVから取得
        follow_keyword = reader_list[0]['follow_keyword'] # フォローするキーワードをCSVから取得
        setting_1 = reader_list[0]['setting_1'] # フォローする条件をCSVから取得
        setting_2 = reader_list[0]['setting_2'] # フォローする条件をCSVから取得

    # csvから過去にフォローしたユーザのIDリストを取得
    with open(follow_history, "r") as f:
        reader = csv.reader(f)
        follow_history_list = [row[1] for row in reader]

    # follow_history.csvに書き込むためにインスタンスを取得
    with open(follow_history,'a') as f:
        csvWriter = csv.writer(f)

        # 各種APIキーをセット
        CONSUMER_KEY = api_key
        CONSUMER_SECRET = api_secret_key
        ACCESS_TOKEN = access_token
        ACCESS_SECRET = access_token_secret

        twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

        # フォロー数の設定
        FOLLOW_NUM = int(follow_num)

        # フォローする検索キーワードの設定
        FOLLOW_KEYWORD = follow_keyword

        # setting_1 = TRUE  ⇒ 過去にフォローした履歴があるユーザはフォローしない
        # setting_1 = FALSE ⇒ 過去にフォローした履歴があるユーザもフォローする
        FOLLOW_SETTING_1 = setting_1

        # setting_2 = TRUE  ⇒ 相互にフォローしていないユーザのみフォローする
        # setting_2 = FALSE ⇒ 相手が自分に片思いでもフォローする
        FOLLOW_SETTING_2 = setting_2

        # 検索キーワードの最大取得数
        SEARCH_MAX_COUNT = 1

        #APIインスタンスを作成
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)
        twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

        # 検索キーワードリスト（複数キーワード対応）
        q_list = [follow_keyword]

        SendTwitterDM("BEFORE", q_list, twitter)

        # 検索キーワードリスト分ループ
        for q in q_list:
            try:
                search_results = api.search(q=q, count=SEARCH_MAX_COUNT)

                for result in search_results:
                    # follow_ini設定に応じて処理を分岐
                    FollowBranch(FOLLOW_SETTING_1, FOLLOW_SETTING_2, follow_history_list, result)

                    # 設定されたフォロー数を超えたらループ終了
                    if follow_count >= FOLLOW_NUM:
                        break

                    # スリープを60秒いれる ⇒ API制限を考慮
                    sleep(60)

            except Exception as e:
                error_count += 1
                # API制限時
                if (str(e) == "[{'code': 32, 'message': 'Could not authenticate you.'}]"):
                    sys.exit()

    SendTwitterDM("AFTER", q_list, twitter)

####################################################################
# 実行タイミング:  毎回
# 機能　　　　　:  follow_iniの設定に応じて処理を分岐
####################################################################
def FollowBranch(FOLLOW_SETTING_1, FOLLOW_SETTING_2, follow_history_list, result):
    global api

    id = result.user._json['id'] # twitterのID
    username = result.user._json['screen_name'] # twitterのスクリーンネーム
    friendship = api.show_friendship(target_screen_name=username) # show_friendshipのインスタンス

    # FOLLOW_SETTING_1 = true  ⇒ 過去にフォローした履歴があるユーザはフォローしない
    if str(FOLLOW_SETTING_1) == "TRUE" :
        # 過去にフォローしたユーザリストにIDが存在しない場合
        if (str(id) in follow_history_list) == False :
            # FOLLOW_SETTING_2 = TRUE  ⇒ 相互にフォローしていないユーザのみフォローする
            if str(FOLLOW_SETTING_2) == "TRUE" :
                NotMutualFollow(id, username)

            # FOLLOW_SETTING_2 = FALSE ⇒ 相手が自分に片思いでもフォローする
            else:
                MutualFollow(id, username)

    # FOLLOW_SETTING_1 = FALSE ⇒ 過去にフォローした履歴があるユーザもフォローする
    else:
        if str(FOLLOW_SETTING_2) == "TRUE" :
            NotMutualFollow(id, username)
        else:
            MutualFollow(id, username)

####################################################################
# 実行タイミング:  setting_2 = TRUE の場合呼び出す
# 機能　　　　　:  お互いフォローしていないユーザをフォローする
####################################################################
def NotMutualFollow(id, username):
    global api
    global csvWriter
    global follow_count

    try:
        friendship = api.show_friendship(target_screen_name=username)

        # お互いフォローしていない場合
        if friendship[1].followed_by == False and friendship[1].following  == False :
            #フォローする
            #api.create_friendship(id)

            # csvにフォローしたユーザの情報を書き込む
            csvWriter.writerow([username,str(id)]) #[スクリーンネーム, ID]

            # フォローした人数をカウント
            follow_count += 1

    except Exception as e:
        sys.exit()

####################################################################
# 実行タイミング:  setting_2 = false の場合呼び出す
# 機能　　　　　:  お互いフォローしていないユーザをフォローする
####################################################################
def MutualFollow(id, username):
    global api
    global csvWriter
    global follow_count

    try:
        api.create_friendship(id)
        csvWriter.writerow([username,str(id)])
        follow_count += 1

    except Exception as e:
        sys.exit()

####################################################################
# 実行タイミング:  フォローツールの開始前、開始後
# 機能　　　　　:  ツールの開始と終了をTwitterのDMで知らせる
####################################################################
def SendTwitterDM(ExecutionTiming, q_list, twitter):
    # おまじない
    headers = {'content-type': 'application/json'}
    url = 'https://api.twitter.com/1.1/direct_messages/events/new.json'

    payload_message_data = ""

    try:
        # DMで送るメッセージを開始前と開始後で可変にする
        if ExecutionTiming == "BEFORE" :
            payload_message_data = ">>フォローツール実行開始"

        elif  ExecutionTiming == "AFTER" :
            payload_message_data = ">>フォローツール実行終了" + "\n検索キーワード-->" + str(q_list) + "\nフォロー数-->" + str(follow_count) + "人"

        payload = {"event":
                  {"type": "message_create",
                   "message_create": {
                       "target": {"recipient_id": "XXXXXX"},# DMを送付したいID
                       "message_data": {"text": payload_message_data ,}# DMで送付したいメッセージ
                   }
                  }
                 }

        # DMを送信
        payload = json.dumps(payload)
        res = twitter.post(url,
                           headers=headers,
                           data=payload)

    except Exception as e:
        sys.exit()

if __name__ == '__main__':
    main()
