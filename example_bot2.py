import discord
import WordWolf
import time
import asyncio
import re

client = discord.Client()
wordwolf = WordWolf.WordWolf()

async def DirectMessage(to, S):
	await to.send(S)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if client.user.mentioned_in(message):
        await message.channel.send('私はワードウルフbotです。操作方法が知りたい場合は「/help」を送信してください。')
    
    if message.content == '/reset':
        print('リセット')
        if wordwolf.config:
            wordwolf.Member = []
            await message.channel.send('参加者設定をリセットしました。')
        else:
            await message.channel.send('リセットするにはまず「/config」と入力し設定モードにしてください。')
    
    if message.content == '/config':
        if wordwolf.nowGame:
            await  message.channel.send('ゲーム中だから待って！！お願い！')
        else:
            if wordwolf.config:
                print('設定モード終了')
                wordwolf.config = False
                await message.channel.send('参加者設定を終了します。')
                if len(wordwolf.Member) == 0:
                    await message.channel.send('現在参加者はいません。')
                else:
                    s = '現在の参加者は、'
                    for m in wordwolf.Member:
                        s = s + m.display_name + 'さん、'
                    s = s + 'の' + (str)(len(wordwolf.Member)) + '名です。'
                    await message.channel.send(s)
            else:
                print('設定モード開始')
                wordwolf.config = True
                await message.channel.send('参加者を設定します。参加する人は「参加します」とコメントしてください。参加をやめる人は「参加しません」とコメントしてください。')    

    if message.content.startswith('/time'):
        if wordwolf.config:
            m = re.findall(r'[0-9][0-9]', message.content)
            if m is None:
                await message.channel.send('時間設定を行う場合は、/timeのあとに設定したい時間(単位は分)を、半角数字を使って2桁の整数値で入力して下さい。')
            else:
                wordwolf.time = int(m[0])
                await message.channel.send('制限時間を' + m[0] + '分に設定しました。')
        else:
            await message.channel.send('時間を変更するにはまず「/config」を送信してください。')

    if message.content == '/check':
        print('参加者確認')
        if len(wordwolf.Member) == 0:
            await message.channel.send('現在参加者はいません。')
        else:
            s = '現在の参加者は、'
            for m in wordwolf.Member:
                s = s + m.display_name + 'さん、'
            s = s + 'の' + (str)(len(wordwolf.Member)) + '名です。'
            await message.channel.send(s)
    
    if message.content == '参加します' and wordwolf.config:
        print('参加者追加')
        if message.author in wordwolf.Member:
            await message.channel.send(message.author.display_name + 'さんは既に参加しています。')
        else:
            wordwolf.Member.append(message.author)
            await message.channel.send(message.author.display_name + 'さんを参加登録しました。')
    
    if message.content == '参加しません' and wordwolf.config:
        print('参加者削除')
        if message.author in wordwolf.Member:
            wordwolf.Member.remove(message.author)
            await message.channel.send(message.author.display_name + 'さん…また遊ぼうね…。一度リストから外しておくよ…。')
        else:
            await message.channel.send(message.author.display_name + 'さんは参加していません。')

    if message.content.startswith('/start'):
        print('ゲーム開始')
        if len(wordwolf.Member) != 0:
            if len(wordwolf.Member) == 1:
                await message.channel.send('一人でやるの…？さみしい人だね。')
            await message.channel.send('ゲームを開始します！！')
            wordwolf.nowGame = True
            MWords = []
            if 'ID' in message.content:
                m = re.findall(r'[0-9]+', message.content)
                if len(m) > 0:
                    id = int(m[0])
                    await message.channel.send('ID指定を受け付けました！' + (str)(id) + '番のお題です！')
                    MWords = wordwolf.startGame(id)
                else:
                    await message.channel.send('ID指定に失敗しました！指定する場合はIDを整数値で入力してください！')
                    MWords = wordwolf.startGame()
            else:
                MWords = wordwolf.startGame()
            wordwolf.config = False
            await message.channel.send(MWords[0])
            for mw in MWords[1]:
                await DirectMessage(mw[0], mw[1])
            await message.channel.send('お題を送りました！頑張ってください！！')
            T = wordwolf.time
            await message.channel.send('制限時間は'+ (str)(T) + '分です！')
            for i in range(T * 6):
                await asyncio.sleep(10)
                if not wordwolf.nowGame:
                    break
                if i % 6 == 5:
                    await message.channel.send('残り'+ (str)(T - (int)((i - 5) / 6) - 1) + '分です！')
            print('ゲーム終了')
            wordwolf.nowGame = False
            wordwolf.result = MWords[1]
            await message.channel.send('ゲーム終了です！お疲れさまでした！！「/result」を送信すると誰がワードウルフだったのかを、「/theme」を送信するとみんなに送られたお題を確認することができます！')
        else:
            await message.channel.send('参加者がいねぇぇぇぇぇぇぇ')

    if message.content == '/end' and wordwolf.nowGame:
        wordwolf.nowGame = False
        await message.channel.send('ゲームを強制終了します！少々お待ちください！！')

    if message.content == '/theme':
        if len(wordwolf.result) != 0:
            await message.channel.send('前の試合に参加者に伝えられたお題を発表します！')
            for m in wordwolf.result:
                await message.channel.send(m[0].display_name + 'さんのお題：' + m[1])
            await message.channel.send('でした！')
        else:
            await message.channel.send('まだ試合してないよ！！')

    if message.content == '/result':
        if len(wordwolf.result) != 0:
            s = '前の試合のワードウルフは'
            for m in wordwolf.result:
                if m[2]:
                    s = s + m[0].display_name + 'さんでした！'
            await message.channel.send( s + '送られたお題を知りたいときは「/theme」を送信して下さい！')
        else:
            await message.channel.send('まだ試合してないよ！！')

    if message.content == '/append':
        print('追加開始')
        if wordwolf.wordnum == 0:
            wordwolf.wordnum = 1
            await message.channel.send('単語を追加します。追加を中止する際は「/cancel」と入力して下さい。一つ目の単語を「//」に続けて入力してください。')
        else:
            await message.channel.send('追加中です。')

    if message.content.startswith('//') and wordwolf.wordnum != 0:
        print('単語追加')
        if wordwolf.wordnum == 1:
            wordwolf.word1 = message.content[2:]
            wordwolf.wordnum = 2
            await message.channel.send('二つ目の単語を「//」に続けて入力してください。')
        elif wordwolf.wordnum == 2:
            wordwolf.word2 = message.content[2:]
            wordwolf.wordnum = 0
            await message.channel.send('追加します')
            response = wordwolf.appendWords()
            await message.channel.send(response)
        else:
            await message.channel.send('やべぇ。バグってるわｗｗｗｗｗ')

    if message.content == '/cancel' and wordwolf.wordnum != 0:
        print('追加中止')
        wordwolf.wordnum = 0
        wordwolf.word1 = ''
        wordwolf.word2 = ''
        await message.channel.send('追加を中止します。')

    if message.content == '/sendlist':
        print('リストを送信します')
        await message.channel.send(file=discord.File('wordslist.db'))

    if message.content == '/help':
        print('ヘルプを送信します')
        await message.channel.send(file=discord.File('help.pdf'))

    # if message.content == '￥追加':
    #     print('追加')
    #     response = wordwolf.appendWords('ドラゴンクエスト', 'ファイナルファンタジー')
    #     print(response)
    #     await message.channel.send(response)


        
    # if message.content.startswith('￥始める'):
    # 	response = wordwolf.startGame()
    # 	print(response)
    # 	if (response == 'すでにゲーム中です'):
    # 		await message.channel.send('すでにゲーム中です')
    # 	else:
    # 		await message.channel.send('ワードウルフをはじめましょう！')


    # if message.content.startswith('￥終わる'):
    # 	response = wordwolf.endGame()
    # 	print(response)
    # 	if (response == ('今はゲームをしていません')):
    # 		await message.channel.send('今はゲームをしていません')
    # 	else:
    # 		await message.channel.send('ゲームを終わります！！')

    # if message.content.startswith('￥DM'):
    # 	print('DMを送ります')
    # 	await DirectMessage(message.author, message.content)
    	

client.run(open("token.txt", "r").read())