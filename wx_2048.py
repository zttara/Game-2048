# -*- coding: utf-8 -*-
# game:wx_2048.py

import wx
import os
import random
import copy

class Window(wx.Window):

    def __init__(self,parent):
        super(Window,self).__init__(parent)
        self.colors = {0:(255,240,245),2:(238, 228, 218),4:(237, 224, 200),8:(242, 177, 121),16:(245, 149, 99),32:(246, 124, 95),64:(246, 94, 59),128:(237, 207, 114),256:(237, 207, 114),512:(237, 207, 114),1024:(237, 207, 114),2048:(237, 207, 114)}
        self.initGame()
        self.initBuffer()


        self.Bind(wx.EVT_SIZE,self.onSize)
        self.Bind(wx.EVT_PAINT,self.onPaint)
        self.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)

    def loadScore(self):
        if os.path.exists("bestscore.ini"):
            ff = open("bestscore.ini")
            self.bstScore = ff.read()
            ff.close()

    def saveScore(self):
        ff = open("bestscore.ini","w")
        ff.write(str(self.bstScore))
        ff.close()

    #initialize the game-----------------------------------------------------------------------
    def initGame(self):
        self.bgFont = wx.Font(50,wx.SWISS,wx.NORMAL,wx.BOLD,face=u"Roboto")
        self.scFont = wx.Font(36,wx.SWISS,wx.NORMAL,wx.BOLD,face=u"Roboto")
        self.smFont = wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,face=u"Roboto")
        self.curScore = 0
        self.bstScore = 0
        self.loadScore()
        self.data = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        #--------------------------------------------------------------
        #find two blocks randomly for the initial numbers 2 and 4.
        count = 0
        while count<2:
            row = random.randint(0,len(self.data)-1)
            col = random.randint(0,len(self.data[0])-1)
            if self.data[row][col]!=0: continue           
            self.data[row][col] = 2 if random.randint(0,1) else 4
            count += 1
        #----------------------------------------------------------------
    
    def initBuffer(self):
        w,h = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(w,h)

    def onSize(self,event):
        self.initBuffer()
        self.drawAll()

    def onPaint(self,event):
        dc = wx.BufferedPaintDC(self,self.buffer)

    def putTile(self):
        available = []
        for row in range(len(self.data)):
            for col in range(len(self.data[0])):
                if self.data[row][col]==0: available.append((row,col))
        if available:
            row,col = available[random.randint(0,len(available)-1)]
            self.data[row][col] = 2 if random.randint(0,1) else 4
            return True
        return False

    #if there are two same numbers, delete one and multiply another one by 2; and then add the scores.
    def update(self,vlist,direct):
        score = 0
        if direct: #up or left
            i = 1
            while i<len(vlist):
                if vlist[i-1]==vlist[i]:
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                    i += 1
                i += 1
        else:
            i = len(vlist)-1
            while i>0:
                if vlist[i-1]==vlist[i]:
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                    i -= 1
                i -= 1      
        #print self.data
        return score
        
    def slideUpDown(self,up):
        score = 0
        numCols = len(self.data[0])
        numRows = len(self.data)
        oldData = copy.deepcopy(self.data)
        
        for col in range(numCols):
            cvl = [self.data[row][col] for row in range(numRows) if self.data[row][col]!=0]

            if len(cvl)>=2:
                score += self.update(cvl,up)
            for i in range(numRows-len(cvl)):
                if up: cvl.append(0)
                else: cvl.insert(0,0)
            for row in range(numRows): self.data[row][col] = cvl[row]
        return oldData!=self.data,score

    def slideLeftRight(self,left):
        score = 0
        numRows = len(self.data)
        numCols = len(self.data[0])
        oldData = copy.deepcopy(self.data)
        
        for row in range(numRows):
            rvl = [self.data[row][col] for col in range(numCols) if self.data[row][col]!=0]

            if len(rvl)>=2:           
                score += self.update(rvl,left)
            for i in range(numCols-len(rvl)):
                if left: rvl.append(0)
                else: rvl.insert(0,0)
            for col in range(numCols): self.data[row][col] = rvl[col]
        return oldData!=self.data,score

    def isGameOver(self):
        copyData = copy.deepcopy(self.data)
        
        flag = False
        if not self.slideUpDown(True)[0] and not self.slideUpDown(False)[0] and not self.slideLeftRight(True)[0] and not self.slideLeftRight(False)[0]:
            flag = True
        if not flag: self.data = copyData
        return flag

    def doMove(self,move,score):
        if move:
            self.putTile()
            self.drawChange(score)
            if self.isGameOver():
                if wx.MessageBox(u"Game Over...Restart? ",u"O(∩_∩)O",wx.YES_NO|wx.ICON_INFORMATION)==wx.YES:
                    bstScore = self.bstScore
                    self.initGame()
                    self.bstScore = bstScore
                    self.drawAll()

    def onKeyDown(self,event):
        keyCode = event.GetKeyCode()
        if keyCode==wx.WXK_UP:
            self.doMove(*self.slideUpDown(True))
        elif keyCode==wx.WXK_DOWN:
            self.doMove(*self.slideUpDown(False))
        elif keyCode==wx.WXK_LEFT:
            self.doMove(*self.slideLeftRight(True))
        elif keyCode==wx.WXK_RIGHT:
            self.doMove(*self.slideLeftRight(False))

    def drawBg(self,dc):
        dc.SetBackground(wx.Brush((255,240,245)))
        dc.Clear()
        dc.SetBrush(wx.Brush((255,182,193)))
        dc.SetPen(wx.Pen((255,182,193)))
        dc.DrawRoundedRectangle(15,150,475,475,5)

    def drawLogo(self,dc):
        dc.SetFont(self.bgFont)
        dc.SetTextForeground((119,110,101))
        dc.SetBrush(wx.Brush((255,192,203)))
        dc.SetPen(wx.Pen((255,192,203)))
        dc.DrawCircle(45,45,40)
        dc.DrawText(u"2",29,11)
        dc.DrawCircle(125,105,40)
        dc.DrawText(u"0",108,73)
        dc.DrawCircle(205,45,40)
        dc.DrawText(u"4",186,11)
        dc.DrawCircle(285,105,40)
        dc.DrawText(u"8",268,73)
   
    def drawLabel(self,dc):
        dc.SetFont(self.smFont)
        dc.SetTextForeground((119,110,101))
        dc.DrawText(u"Challenge!",380,114) 
        dc.DrawText(u"How to play: \nUse the key of ↑、↓、←、→ to move the tiles, and \ntwo tiles with the same number will change into one.\nWhen the number 2048 is gotted, you win!!!",15,630)

    #draw the score
    def drawScore(self,dc):
        dc.SetFont(self.smFont)
        scoreLabelSize = dc.GetTextExtent(u"SCORE")
        bestLabelSize = dc.GetTextExtent(u"BEST")
        curScoreBoardMinW = 15*2+scoreLabelSize[0]
        bstScoreBoardMinW = 15*2+bestLabelSize[0]
        curScoreSize = dc.GetTextExtent(str(self.curScore))
        bstScoreSize = dc.GetTextExtent(str(self.bstScore))
        curScoreBoardNedW = 10+curScoreSize[0]
        bstScoreBoardNedW = 10+bstScoreSize[0]
        curScoreBoardW = max(curScoreBoardMinW,curScoreBoardNedW)
        bstScoreBoardW = max(bstScoreBoardMinW,bstScoreBoardNedW)
        dc.SetBrush(wx.Brush((221,160,221)))
        dc.SetPen(wx.Pen((221,160,221)))
        dc.DrawRoundedRectangle(505-15-bstScoreBoardW,40,bstScoreBoardW,50,3)
        dc.DrawRoundedRectangle(505-15-bstScoreBoardW-5-curScoreBoardW,40,curScoreBoardW,50,3)
        dc.SetTextForeground((0,0,0))
        dc.DrawText(u"BEST",505-15-bstScoreBoardW+(bstScoreBoardW-bestLabelSize[0])/2,48)
        dc.DrawText(u"SCORE",505-15-bstScoreBoardW-5-curScoreBoardW+(curScoreBoardW-scoreLabelSize[0])/2,48)
        dc.SetTextForeground((0,0,0))
        dc.DrawText(str(self.bstScore),505-15-bstScoreBoardW+(bstScoreBoardW-bstScoreSize[0])/2,68)
        dc.DrawText(str(self.curScore),505-15-bstScoreBoardW-5-curScoreBoardW+(curScoreBoardW-curScoreSize[0])/2,68)
    
    #draw the tiles according to the data, and the color will change with different data.
    def drawTiles(self,dc):
        dc.SetFont(self.scFont)
        for row in range(4):
            for col in range(4):
                value = self.data[row][col]
                color = self.colors[value]
                if value==2 or value==4:
                    dc.SetTextForeground((119,110,101))
                else:
                    dc.SetTextForeground((255,255,255))
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))
                dc.DrawRoundedRectangle(30+col*115,165+row*115,100,100,2)
                size = dc.GetTextExtent(str(value))
                while size[0]>100-15*2:
                    self.scFont = wx.Font(self.scFont.GetPointSize()*4/5,wx.SWISS,wx.NORMAL,wx.BOLD,face=u"Roboto")
                    dc.SetFont(self.scFont)
                    size = dc.GetTextExtent(str(value))
                if value!=0: dc.DrawText(str(value),30+col*115+(100-size[0])/2,165+row*115+(100-size[1])/2)

    def drawAll(self):
        dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
        self.drawBg(dc)
        self.drawLogo(dc)
        self.drawLabel(dc)
        self.drawScore(dc)
        self.drawTiles(dc)

    def drawChange(self,score):
        dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
        if score:
            self.curScore += score
            if self.curScore > self.bstScore:
                self.bstScore = self.curScore
            self.drawScore(dc)
        self.drawTiles(dc)

        
class Frame(wx.Frame):

    def __init__(self,title):
        super(Frame,self).__init__(None,-1,title,style=wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX^wx.RESIZE_BORDER)
        self.setIcon()
        self.window = Window(self)
        self.Bind(wx.EVT_CLOSE,self.onClose)

    def onClose(self,event):
        self.window.saveScore()
        self.Destroy()

    def setIcon(self):
        icon = wx.Icon("icon.ico",wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)


class App(wx.App):

    def OnInit(self):
        self.frame = Frame(u"Game_2048_python")
        self.frame.SetClientSize((505,700))
        self.frame.Center()
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = App()
    app.MainLoop()