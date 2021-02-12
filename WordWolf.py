import discord
import random
import sqlite3

class WordWolf:
	def __init__(self):
		# with open('wordslist.txt', encoding='utf-8') as f:
		# 	self.wl = [s.strip() for s in f.readlines()]
		# self.wordList = []
		# for i in range((int)(len(self.wl) / 2)):
		# 	self.wordList.append((self.wl[2 * i], self.wl[2 * i + 1]))
		# 謎のこめんと
		self.config = False
		self.nowGame = False
		self.wordnum = 0
		self.Member = []
		self.word1 = ''
		self.word2 = ''
		self.time = 5
		self.result = []

	def startGame(self, ID=None):
		conn = sqlite3.connect('wordslist.db')
		c = conn.cursor()
		s = 'お題はランダムです！'
		if ID is not None:
			c.execute("SELECT word1, word2 FROM wordslist WHERE ID = ?",(ID,))
			wordslist = c.fetchall()
			if len(wordslist) == 0:
				c.execute("SELECT word1, word2 FROM wordslist")
				wordslist = c.fetchall()
				s = 'ID検索に失敗しました！お題はランダムになります！'
			else:
				s = 'ID検索に成功しました！'
		else:
			c.execute("SELECT word1, word2 FROM wordslist")
			wordslist = c.fetchall()
		conn.commit()
		conn.close()
		MWlist = []
		l = random.randrange(0, len(wordslist))
		j = random.randrange(0, len(self.Member))
		t = random.randrange(0, 2)
		i = 0
		for m in self.Member:
			if(i == j):
				if (t == 0):
					MWlist.append((m, wordslist[l][0], True))
				else:
					MWlist.append((m, wordslist[l][1], True))
			else:
				if (t == 0):
					MWlist.append((m, wordslist[l][1], False))
				else:
					MWlist.append((m, wordslist[l][0], False))
			i += 1
		return (s, MWlist)

	def appendWords(self):
		conn = sqlite3.connect('wordslist.db')
		c = conn.cursor()
		c.execute('SELECT word1, word2 FROM wordslist')
		wordslist = c.fetchall()
		if (self.word1, self.word2) in wordslist or (self.word2, self.word1) in wordslist:
			self.word1 = ''
			self.word2 = ''
			conn.commit()
			conn.close()
			return 'もうあるよ！'
		else:	
			# with open('wordslist.txt', mode='a', encoding='utf-8') as f:
			# 	f.write(self.word1 + '\n')
			# 	f.write(self.word2 + '\n')
			# self.wordList.append((self.word1, self.word2))
			c.execute("INSERT INTO wordslist (word1, word2) VALUES (?, ?)", (self.word1, self.word2))
			c.execute("SELECT ID FROM wordslist WHERE word1 = ? AND word2 = ?", (self.word1, self.word2))
			ID = c.fetchone()
			conn.commit()
			conn.close()
			self.word1 = ''
			self.word2 = ''
			return ('追加したよ！！IDは' + (str)(ID[0]) + 'だよ！！')
