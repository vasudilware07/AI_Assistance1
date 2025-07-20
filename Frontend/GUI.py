from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, 
                             QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, 
                         QPixmap, QTextBlockFormat, QPalette, QBrush, QLinearGradient)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "when", "where", "who", "which", "why", "can you", "whom", "whose", "what's", "where's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(rf"{TempDirPath}/Mic.data", "w", encoding="utf-8") as file:
            file.write(Command)
    except Exception as e:
        print(f"Error setting microphone status: {e}")

def GetMicrophoneStatus():
    try:
        with open(rf"{TempDirPath}/Mic.data", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        SetMicrophoneStatus("False")
        return "False"
    except Exception as e:
        print(f"Error getting microphone status: {e}")
        return "False"

def SetAssistantStatus(Status):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
            file.write(Status)
    except Exception as e:
        print(f"Error setting assistant status: {e}")

def GetAssistantStatus():
    try:
        with open(rf"{TempDirPath}/Status.data", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        SetAssistantStatus("Ready")
        return "Ready"
    except Exception as e:
        print(f"Error getting assistant status: {e}")
        return "Ready"

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDictonaryPath(Filename):
    Path = rf"{GraphicsDirPath}\{Filename}"
    return Path

def TempDictonaryPath(Filename):
    Path = rf"{TempDirPath}\{Filename}"
    return Path

def ShowTextToScreen(Text):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(rf"{TempDirPath}\Responses.data", "w", encoding="utf-8") as file:
            file.write(Text)
    except Exception as e:
        print(f"Error showing text to screen: {e}")

class ModernButton(QPushButton):
    def __init__(self, text="", icon_path="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(20, 20))
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            ModernButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            ModernButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #408acd);
            }
            ModernButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3580d2, stop:1 #2670ad);
            }
        """)

class AnimatedMicButton(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.toggled = True
        self.is_listening = False
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"scale")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Load initial icon
        self.load_icon(GraphicsDictonaryPath("Mic_on.png") if os.path.exists(GraphicsDictonaryPath("Mic_on.png")) else None)
        
        # Add glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(20)
        self.glow_effect.setColor(QColor(74, 144, 226, 150))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def load_icon(self, path, width=60, height=60):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            scaled_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
        else:
            # Create a default microphone icon if file doesn't exist
            self.create_default_mic_icon(width, height)

    def create_default_mic_icon(self, width, height):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw microphone shape
        color = QColor(74, 144, 226) if self.toggled else QColor(200, 200, 200)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        
        # Mic body
        painter.drawRoundedRect(width//4, height//6, width//2, height//2, 8, 8)
        # Mic base
        painter.drawRect(width//3, height*2//3, width//3, height//6)
        # Mic stand
        painter.drawRect(width//2-2, height*5//6, 4, height//12)
        
        painter.end()
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_icon()
            # Add click animation
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.9)
            self.animation.finished.connect(lambda: self.animation.setEndValue(1.0))
            self.animation.start()

    def toggle_icon(self):
        if self.toggled:
            self.load_icon(GraphicsDictonaryPath("Mic_off.png") if os.path.exists(GraphicsDictonaryPath("Mic_off.png")) else None)
            MicButtonClosed()
            self.glow_effect.setColor(QColor(200, 200, 200, 100))
        else:
            self.load_icon(GraphicsDictonaryPath("Mic_on.png") if os.path.exists(GraphicsDictonaryPath("Mic_on.png")) else None)
            MicButtonInitialed()
            self.glow_effect.setColor(QColor(74, 144, 226, 150))
        
        self.toggled = not self.toggled

    @pyqtProperty(float)
    def scale(self):
        return self._scale if hasattr(self, '_scale') else 1.0

    @scale.setter
    def scale(self, value):
        self._scale = value
        size = int(80 * value)
        self.resize(size, size)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        max_gif_size_W = int(screen_width / 4)
        max_gif_size_H = int(max_gif_size_W / 16 * 9)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 40, 100)
        layout.setSpacing(20)
        
        # Chat area with modern styling
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        
        # Modern chat styling
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 15px;
                color: white;
                selection-background-color: rgba(74, 144, 226, 0.3);
            }
        """)
        
        layout.addWidget(self.chat_text_edit)
        
        # Bottom section with GIF and status
        bottom_section = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            padding: 10px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            margin-right: 20px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(40)
        
        # GIF section
        if os.path.exists(GraphicsDictonaryPath("Jarvis.gif")):
            self.gif_label = QLabel()
            self.gif_label.setStyleSheet("border: none; border-radius: 10px;")
            movie = QMovie(GraphicsDictonaryPath("Jarvis.gif"))
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
            bottom_section.addWidget(self.status_label, 1)
            bottom_section.addWidget(self.gif_label, 2)
        else:
            bottom_section.addWidget(self.status_label, 1)
        
        layout.addLayout(bottom_section)
        
        self.setStyleSheet("background-color: transparent;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        # Font setup
        font = QFont("Segoe UI", 12)
        self.chat_text_edit.setFont(font)
        
        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)  # Reduced frequency for better performance
        
        # Modern scrollbar styling
        self.chat_text_edit.setStyleSheet(self.chat_text_edit.styleSheet() + """
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(74, 144, 226, 0.7);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(74, 144, 226, 1.0);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDictonaryPath("Responses.data"), "r", encoding="utf-8") as file:
                messages = file.read()
                
                if messages and str(old_chat_message) != str(messages):
                    self.addMessage(message=messages, color="#E3F2FD", is_assistant=True)
                    old_chat_message = messages
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading messages: {e}")

    def updateStatus(self):
        try:
            status = GetAssistantStatus()
            self.status_label.setText(status if status else "Ready")
        except Exception as e:
            print(f"Error updating status: {e}")

    def addMessage(self, message, color="#FFFFFF", is_assistant=False):
        cursor = self.chat_text_edit.textCursor()
        cursor.movePosition(cursor.End)
        
        # Add some spacing
        cursor.insertText("\n" if cursor.position() > 0 else "")
        
        # Format message
        format_msg = QTextCharFormat()
        format_block = QTextBlockFormat()
        
        if is_assistant:
            format_msg.setForeground(QColor("#4A90E2"))
            format_block.setLeftMargin(20)
            prefix = f"{Assistantname}: "
        else:
            format_msg.setForeground(QColor("#FFFFFF"))
            format_block.setRightMargin(20)
            prefix = "You: "
        
        format_block.setTopMargin(10)
        format_block.setBottomMargin(5)
        
        cursor.setCharFormat(format_msg)
        cursor.setBlockFormat(format_block)
        cursor.insertText(prefix + message + "\n")
        
        # Auto-scroll to bottom
        scrollbar = self.chat_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 100)
        main_layout.setSpacing(30)
        
        # Welcome section
        welcome_layout = QVBoxLayout()
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel(f"Welcome to {Assistantname}")
        title_label.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        subtitle_label = QLabel("Your AI Assistant is ready to help")
        subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            font-size: 18px;
            margin-bottom: 30px;
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        welcome_layout.addWidget(title_label)
        welcome_layout.addWidget(subtitle_label)
        
        # GIF section (if available)
        if os.path.exists(GraphicsDictonaryPath("Enticing.gif")):
            gif_label = QLabel()
            movie = QMovie(GraphicsDictonaryPath("Enticing.gif"))
            gif_label.setMovie(movie)
            max_gif_size_H = min(int(screen_width / 16 * 9), 400)
            max_gif_size_W = min(screen_width - 100, 600)
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            gif_label.setAlignment(Qt.AlignCenter)
            movie.start()
            welcome_layout.addWidget(gif_label)
        
        main_layout.addLayout(welcome_layout)
        
        # Controls section
        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignCenter)
        
        # Status label
        self.status_label = QLabel("Ready to listen...")
        self.status_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            padding: 15px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            margin-bottom: 20px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Microphone button
        self.mic_button = AnimatedMicButton()
        
        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        
        main_layout.addLayout(controls_layout)
        
        self.setLayout(main_layout)
        self.setFixedSize(screen_width, screen_height)
        
        # Background gradient
        self.setStyleSheet("""
            InitialScreen {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000428, stop:1 #004e92);
            }
        """)
        
        # Timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)

    def updateStatus(self):
        try:
            status = GetAssistantStatus()
            self.status_label.setText(status if status else "Ready to listen...")
        except Exception as e:
            print(f"Error updating status: {e}")

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        self.setLayout(layout)
        self.setFixedSize(screen_width, screen_height)
        
        # Background gradient
        self.setStyleSheet("""
            MessageScreen {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000428, stop:1 #004e92);
            }
        """)

class CustomTopBar(QWidget):
    def __init__(self, parent, stack_widget):
        super().__init__(parent)
        self.stack_widget = stack_widget
        self.offset = None
        self.initUI()

    def initUI(self):
        self.setFixedHeight(60)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 5, 15, 5)
        
        # Left section - App title
        title_label = QLabel(f"{str(Assistantname).upper()} AI")
        title_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
        """)
        
        # Center section - Navigation
        nav_layout = QHBoxLayout()
        nav_layout.setAlignment(Qt.AlignCenter)
        
        self.home_button = ModernButton("🏠 Home")
        self.chat_button = ModernButton("💬 Chat")
        
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.chat_button)
        
        # Right section - Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setAlignment(Qt.AlignRight)
        
        minimize_btn = QPushButton("−")
        maximize_btn = QPushButton("□")
        close_btn = QPushButton("✕")
        
        for btn in [minimize_btn, maximize_btn, close_btn]:
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """)
        
        close_btn.setStyleSheet(close_btn.styleSheet().replace(
            "rgba(255, 255, 255, 0.1)", "rgba(220, 53, 69, 0.8)"
        ).replace(
            "rgba(255, 255, 255, 0.2)", "rgba(220, 53, 69, 1.0)"
        ))
        
        controls_layout.addWidget(minimize_btn)
        controls_layout.addWidget(maximize_btn)
        controls_layout.addWidget(close_btn)
        
        # Add all sections
        main_layout.addWidget(title_label)
        main_layout.addStretch()
        main_layout.addLayout(nav_layout)
        main_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        self.setLayout(main_layout)
        
        # Background
        self.setStyleSheet("""
            CustomTopBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.1), stop:1 rgba(255, 255, 255, 0.05));
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        # Connect signals
        self.home_button.clicked.connect(lambda: self.stack_widget.setCurrentIndex(0))
        self.chat_button.clicked.connect(lambda: self.stack_widget.setCurrentIndex(1))
        minimize_btn.clicked.connect(self.parent().showMinimized)
        maximize_btn.clicked.connect(self.toggle_maximize)
        close_btn.clicked.connect(self.parent().close)

    def toggle_maximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.offset:
            self.parent().move(event.globalPos() - self.offset)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Central widget setup
        stacked_widget = QStackedWidget(self)
        
        # Create screens
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        
        # Window setup
        self.setGeometry(100, 100, min(screen_width-200, 1400), min(screen_height-200, 900))
        self.setCentralWidget(stacked_widget)
        
        # Top bar
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        
        # Window styling
        self.setStyleSheet("""
            MainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000428, stop:1 #004e92);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
        """)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    
    # Set application-wide dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(GraphicalUserInterface())