from PyQt5.QtWidgets import QWidget,QDesktopWidget,QMainWindow,QLabel,QPushButton,QStatusBar,QDialog,QApplication
from PyQt5.QtGui import  QBitmap,QPainter,QPen,QBrush,QFont,QMouseEvent,QCursor
from PyQt5.QtCore import Qt,QPoint,QRect,QEvent,pyqtSignal

import gobject
from myutils.config import globalconfig
from gui.resizeablemainwindow import Mainw
import windows
class rangeadjust(Mainw) :
 
    def __init__(self,parent):

        super(rangeadjust, self).__init__(parent) 
        self.label = QLabel(self) 
        self.setstyle()
        self.drag_label = QLabel(self)
        self.drag_label.setGeometry(0, 0, 4000, 2000)
        self._isTracking=False 
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground) 

        for s in self.cornerGrips: 
            s.raise_()
    def setstyle(self):
        self.label.setStyleSheet(" border:%spx solid %s; background-color: rgba(0,0,0, 0.01)"   %(globalconfig['ocrrangewidth'],globalconfig['ocrrangecolor'] ))
    def mouseMoveEvent(self, e ) :  
        if self._isTracking: 
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos) 
    def mousePressEvent(self, e ) : 
            if e.button() == Qt.LeftButton :
                self._isTracking = True
                self._startPos = QPoint(e.x(), e.y()) 
    def mouseReleaseEvent(self, e ) : 
            if e.button() == Qt.LeftButton:
                self._isTracking = False
                self._startPos = None
                self._endPos = None  
    def moveEvent(self,e):
                rect = self.geometry() 
                try:    
                    if self.isVisible():
                        gobject.baseobject.textsource.rect=[(rect.left(),rect.top()),(rect.right(),rect.bottom())]  
                except:
                    pass
    def enterEvent(self, QEvent) :  
        self.drag_label.setStyleSheet("background-color:rgba(0,0,0, 0.1)") 
    def leaveEvent(self, QEvent): 
        self.drag_label.setStyleSheet("background-color:none")  
    def resizeEvent(self, a0 ) :
          
         self.label.setGeometry(0, 0, self.width(), self.height())  
         rect = self.geometry() 
         try:    
             if self.isVisible():
                 gobject.baseobject.textsource.rect=[(rect.left(),rect.top()),(rect.right(),rect.bottom())]  
         except:pass
         super(rangeadjust, self).resizeEvent(a0)  


class rangeselct(QMainWindow) :
    def __init__(self, parent ) :

        super(rangeselct, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)#|Qt.WindowStaysOnTopHint  )
        
    def reset(self):
        self.setStyleSheet('''background-color:black; ''')
        self.setWindowOpacity(globalconfig['OCR_mask_Opacity'])
        num_screens = QDesktopWidget().screenCount()
        x,y,x2,y2=9999,9999,0,0
        for i in range(num_screens):
            _rect=QDesktopWidget().screenGeometry(i)
            x=min(x,_rect.x())
            y=min(y,_rect.y())
            x2=max(x2,_rect.x()+_rect.width())
            y2=max(y2,_rect.y()+_rect.height()) 
        self.setGeometry(x,y,x2-x,y2-y)
        self.setCursor(Qt.CrossCursor)
        self.image=QApplication.primaryScreen().grabWindow(0,x,y,x2-x,y2-y)
        self.is_drawing = False
        self.setMouseTracking(True)
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.startauto=False
        self.clickrelease=False
    def immediateend(self):
        try:
            
            self.close() 
            
            self.callback(self.getRange() )  
        except:
            pass
    def paintEvent(self, event):  
             
            if self.is_drawing:
                
                pp = QPainter(self )
                pen = QPen()
                pen.setStyle(Qt.NoPen)
                pp.setPen(pen)
                brush = QBrush(Qt.white)
                pp.setBrush(brush)
                #print(QRect(self.start_point, self.end_point),self.image.size())
                #pp.drawRect(QRect(self.start_point, self.end_point))
                _x1=self.start_point.x()
                _y1=self.start_point.y()
                _x2=self.end_point.x()
                _y2=self.end_point.y()
                _sp=QPoint(min(_x1,_x2),min(_y1,_y2))
                _ep=QPoint(max(_x1,_x2),max(_y1,_y2))
                pp.drawPixmap(QRect(_sp,_ep),self.image.copy(QRect(_sp,_ep)))
    def mousePressEvent(self, event) : 
            if event.button() == Qt.LeftButton:
                if self.clickrelease:
                    self.clickrelease=False
                    self.mouseReleaseEvent(event)
                else:
                    self.start_point = event.pos()
                    self.end_point = self.start_point
                    self.is_drawing = True 
    def mouseMoveEvent(self, event) : 
            
            if self.startauto and self.is_drawing==False:
                self.is_drawing=True
                self.end_point = self.start_point=event.pos()
                self.startauto=False
            if self.is_drawing:
                self.end_point = event.pos()
                self.update() 
    def getRange(self) :
        start_point=self.mapToGlobal(self.start_point)
        end_point=self.mapToGlobal(self.end_point)
        x1,y1,x2,y2=(start_point.x(),start_point.y() ,end_point.x(),end_point.y()) 
        
        x1,x2=min(x1,x2),max(x1,x2)
        y1,y2=min(y1,y2),max(y1,y2)

        return (((x1,y1),(x2,y2)))
    def mouseReleaseEvent(self, event): 
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            
            self.close() 
            self.callback(self.getRange() )  

screen_shot_ui=None
def rangeselct_function(parent,callback,clickrelease,startauto):
        global screen_shot_ui
        if screen_shot_ui is None:
            screen_shot_ui =rangeselct(parent)
        screen_shot_ui.reset()
        screen_shot_ui.show()
        screen_shot_ui.callback=callback
        windows.SetFocus(int(screen_shot_ui.winId() )   )
         
        screen_shot_ui.startauto=startauto
        screen_shot_ui.clickrelease=clickrelease
from myutils.wrapper import Singleton_close
@Singleton_close
class moveresizegame(QDialog) :

    def __init__(self, parent,hwnd ): 
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        self.setWindowTitle("调整窗口  "+ windows.GetWindowText(hwnd))
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint  )
        # self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setWindowOpacity(0.5)

        self.setMouseTracking(True)
         
        self._isTracking=False
         
 
        self.hwnd=hwnd
        self.maxed=False
        if self.hwnd==0:
            self.close()
        try:
            rect=windows.GetWindowRect(self.hwnd)  
            if rect:
                self.setGeometry(rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1])
            self.show()
        except:
            self.close()
    def moveEvent(self, a0 ) -> None:
        rect = self.geometry() 
        if self.isMaximized()==False:
            try:
                windows.MoveWindow(self.hwnd,  rect.left(),rect.top(),rect.right()-rect.left(), rect.bottom()-rect.top(),  False)
            except:
                pass
        return super().moveEvent(a0)
     
    def closeEvent(self, a0 ) -> None:
        gobject.baseobject.moveresizegame=None
        return super().closeEvent(a0)
    def mouseMoveEvent(self, e ) :  
        if self._isTracking: 
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos) 
            rect = self.geometry() 
            if self.isMaximized()==False:
                try:
                    windows.MoveWindow(self.hwnd,  rect.left(),rect.top(),rect.right()-rect.left(), rect.bottom()-rect.top(),  False)
                except:
                    pass
    def mousePressEvent(self, e ) : 
            if e.button() == Qt.LeftButton :
                self._isTracking = True
                self._startPos = QPoint(e.x(), e.y()) 
    def mouseReleaseEvent(self, e ) : 
            if e.button() == Qt.LeftButton:
                self._isTracking = False
                self._startPos = None
                self._endPos = None 
    def changeEvent(self, a0 ) -> None:
        if a0.type() == QEvent.WindowStateChange:
            try:
                if self.isMaximized():
                    windows.ShowWindow(self.hwnd,windows.SW_MAXIMIZE) 
                else:  
                    windows.ShowWindow(self.hwnd,windows.SW_SHOWNORMAL)
            except:
                pass
    def resizeEvent(self, a0 ) :
        if self.isMaximized()==False: 
            rect = self.geometry()
            try:
                windows.MoveWindow(self.hwnd,  rect.left(),rect.top(),rect.right()-rect.left(), rect.bottom()-rect.top(),  False)
            except:
                pass
            