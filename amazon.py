from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import time
import random
import re

amazon = 'https://www.amazon.co.jp'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def get_info(item):
        try:
                time.sleep(1 + 5*random.random())
                url = amazon + item.a.get('href')
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content, features='lxml')
                spec = soup.find_all('table', {'id':'technicalSpecifications_section_1'})[0].find_all('td', {'class':'a-span7'})
                brand = spec[0].text.strip()
                model = spec[1].text.strip()
                print(' Brand:', brand)
                print(' Model:', model)
                price = soup.find('span', {'id':'priceblock_ourprice'})
                if price == None:
                        price = soup.find('span', {'id':'priceblock_saleprice'})
                if price == None:
                        price = soup.find('span', {'id':'priceblock_dealprice'})
                price = price.text[1:].replace(',','')
                print(' Price:', price)
                ranks = soup.find('li', {'id':'SalesRank'})
                rank = re.sub(r'\D', '', re.findall('-.+位',ranks.text)[0])
                print(' Rank:', rank)
                review = soup.find('span', {'id':'acrCustomerReviewText'})
                rate = soup.find('span', {'id':'acrPopover'})
                if review == None:
                        review = 0
                        rate = 0
                else:
                        review = re.sub(r'\D', '', review.text.strip())
                        rate = re.findall('[0-9].[0-9]', rate.text.strip())[0]
                print(' Review:', review)
                print(' Rate:', rate)
                info = [brand, model, price, rank, review, rate]
                #print('info: ', info)
                return info
        except Exception as e:
                print('Faild!!')
                print(e)
                #print(spec)
                info = ['','','','','','']
        finally:
                return info

def search_amazon(search_category, search_word, get_pages):
        #引数の中に空白があったとき、空白を+に置き換える
        words = search_word.split(' ')
        search_words = words[0]
        for i in range(1, len(words)):
                search_words = search_words + '+' + words[i]

        #スクレイピングするサイトのURLを作成
        url = amazon + '/s?k=' + search_words + '&i=' + search_category + '&__mk_ja_JP=カタカナ&ref=nb_sb_noss' 

        #リストを作成
        columns = ['Brand', 'Model', 'Price', 'Rank', 'Review', 'Rate', 'Image']
        df = pd.DataFrame(columns=columns)

        #ページ番号
        page = 1
        #ページ数が足りないときはエラーではなく、そのページ以降はないことを知らせてくれる
        try:
                while page < get_pages + 1:
                        counter = 1
                        #何ページ目を取得している最中なのか表示
                        print('Getting page' , page)

                        #作成したURLからHTMLを取得
                        response = requests.get(url, headers=headers)
                        #print(response)
                        #BeautifulSoupの初期化
                        soup = BeautifulSoup(response.content, features='lxml')
                        #どこの部分を取得するか指定
                        #print(soup)
                        items = soup.find_all('span', {'data-component-type':'s-product-image', 'class':'rush-component'})
                        print('Num of Items:', len(items))
                        #いくつかの商品を同時に取得しているので商品ごとに商品名と値段とURLを取得
                        for item in items:
                                print('Item', counter)
                                img_url = item.img.get('src')
                                imgfilename = img_url.split('/')[-1]
                                img = requests.get(img_url)
                                with open('./img/' + imgfilename, 'wb') as f:
                                        f.write(img.content)
                                info = get_info(item)
                                info.append(imgfilename)
                                t_df = pd.DataFrame(info, index=columns).T
                                df = df.append(t_df)
                                print(' ImgFile:', imgfilename)
                                counter = counter + 1

                        #ページの下の方の「次のページ」のURLを取得
                        NextUrl = soup.find('li', {'class':'a-last'})
                        Url = NextUrl.a.get('href')

                        #そのままでは次のページに行けないのでちゃんとしたものに変更
                        url = amazon + Url

                        #次のページに行くので変数pageの値を1大きくする
                        page += 1
        except Exception as e:
                #取得しようと思ったページ数まで到達する前に終わったらそのページ以降はなかったと出力
                print(e)
                print('Cannot get', str(page+1))
        finally:
                #保存するcsvのファイル名を決める
                filename = 'amazon_' + search_word + '.csv'

                #作成したリストをcsvへ
                df.to_csv(filename, index=False)

                #終わったことを出力
                print('finish')

search_amazon('カテゴリ', 'キーワード', 2)
