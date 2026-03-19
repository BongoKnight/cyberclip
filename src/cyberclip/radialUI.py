"""
CyberClip Vertical Menu - Modern Qt5 Implementation

A clean vertical menu for quick clipboard parsing and actions.
Triggered with Ctrl+Alt+M, displays parsed data types as alphabetically sorted rectangular buttons.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import threading
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache, partial
from math import cos, radians, sin
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════
# DEPENDENCY CHECKS
# ══════════════════════════════════════════════════════════════════════════

_MISSING_DEPS = []

try:
    import keyboard
except ImportError:
    keyboard = None
    _MISSING_DEPS.append("keyboard")

try:
    import pyperclip
except ImportError:
    pyperclip = None
    _MISSING_DEPS.append("pyperclip")

try:
    from PyQt5.QtCore import (
        QCoreApplication, QEvent, QPoint, QPointF, QPropertyAnimation, QRect, QRectF,
        Qt, pyqtProperty, QEasingCurve
    )
    from PyQt5.QtGui import (
        QBrush, QColor, QConicalGradient, QFont, QFontMetrics, QPainter,
        QPainterPath, QPen, QPolygonF, QRadialGradient
    )
    from PyQt5.QtWidgets import (
        QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
        QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton,
        QScrollArea, QTextEdit, QVBoxLayout, QWidget
    )
except ImportError:
    _MISSING_DEPS.extend(["PyQt5"])

# Toast notifications - platform specific
_TOAST_AVAILABLE = False
try:
    # Try win11toast first (Windows)
    from win11toast import toast
    _TOAST_AVAILABLE = True
except ImportError:
    # Fallback to print for Linux/Mac
    def toast(message: str):
        """Fallback toast for non-Windows platforms."""
        print(f"[CyberClip] {message}")
    _TOAST_AVAILABLE = False

try:
    from cyberclip import userTypeParser, userAction
    from cyberclip.clipParser import clipParser
    from cyberclip.tui.TagsInput import TagsInput
except ImportError as e:
    print(f"Failed to import from cyberclip package: {e}")
    try:
        import userTypeParser, userAction
        from clipParser import clipParser
    except ImportError as e2:
        print(f"Failed to import clipParser: {e2}")
        raise
    try:
        from tui.TagsInput import TagsInput
    except ImportError:
        TagsInput = None


# ══════════════════════════════════════════════════════════════════════════
# GLOBAL PARSER (loaded once like flask_app.py)
# ══════════════════════════════════════════════════════════════════════════

_parser: clipParser | None = None

def get_parser() -> clipParser:
    """Get or create the global clipParser instance."""
    global _parser
    if _parser is None:
        _parser = clipParser()
        _parser.load_all()
    return _parser


# ══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════════

def async_toast(message: str):
    """
    Show toast notification in background thread to avoid blocking UI.

    Args:
        message: The notification message to display
    """
    def _show():
        try:
            toast(message)
        except Exception as e:
            print(f"Toast notification failed: {e}")

    threading.Thread(target=_show, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════
# CONFIGURATION & CONSTANTS
# ══════════════════════════════════════════════════════════════════════════

class Config:
    """Configuration constants for the menu."""

    # Dimensions
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 40
    BUTTON_SPACING = 4
    MENU_PADDING = 8
    MAX_BUTTONS = 12

    # Colors
    BG_COLOR = QColor(30, 35, 45, 220)
    BUTTON_COLOR = QColor(45, 50, 60, 200)
    HOVER_COLOR = QColor(88, 166, 255, 180)
    TEXT_COLOR = QColor(230, 235, 245)
    BORDER_COLOR = QColor(100, 110, 130, 150)

    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE = 10
    FONT_WEIGHT = QFont.Medium

    # Animation
    FADE_DURATION = 150
    SCALE_DURATION = 200

    # Behavior
    KEYBOARD_SHORTCUT = "ctrl+alt+m"
    MIN_BUTTONS = 1


# ══════════════════════════════════════════════════════════════════════════
# COLOR UTILITIES
# ══════════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=128)
def generate_type_color(type_name: str) -> QColor:
    """
    Generate a consistent, visually appealing color for a data type.

    Uses golden ratio for even distribution in HSV space.

    Args:
        type_name: The name of the data type

    Returns:
        QColor object with consistent hue for this type
    """
    # Use hash for consistency
    hash_val = hash(type_name)

    # Golden ratio conjugate for even distribution
    golden_ratio = 0.618033988749895
    hue = (hash_val * golden_ratio) % 1.0

    # Create color with good saturation and value
    color = QColor()
    color.setHsvF(hue, 0.65, 0.85)
    color.setAlpha(200)

    return color


def create_gradient(center: QPoint, inner_color: QColor, outer_color: QColor,
                    radius: int) -> QRadialGradient:
    """Create a radial gradient from center."""
    gradient = QRadialGradient(center, radius)
    gradient.setColorAt(0, inner_color)
    gradient.setColorAt(1, outer_color)
    return gradient


# ══════════════════════════════════════════════════════════════════════════
# GEOMETRY UTILITIES
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class ButtonGeometry:
    """Geometry data for a rectangular button."""
    rect: QRectF

    def create_path(self) -> QPainterPath:
        """Create the button path for drawing and hit testing."""
        path = QPainterPath()
        path.addRoundedRect(self.rect, 6, 6)
        return path

    def text_position(self) -> QPointF:
        """Calculate optimal text position (center of button)."""
        return self.rect.center()

    def badge_position(self) -> QPointF:
        """Calculate badge position (right side of button)."""
        return QPointF(self.rect.right() - 25, self.rect.center().y())


# ══════════════════════════════════════════════════════════════════════════
# TAGS INPUT WIDGET
# ══════════════════════════════════════════════════════════════════════════

class TagsInputWidget(QWidget):
    """
    Qt-based tags input widget for parameter dialog.

    Allows users to add, remove, and manage tags interactively.
    """

    def __init__(self, default_tags: List[str] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.tags = set(default_tags) if default_tags else set()
        self.param_type = 'tags'

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a tag and press Enter...")
        self.input_field.returnPressed.connect(self._add_tag)
        layout.addWidget(self.input_field)

        # Tags container (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(100)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #30363d;
                border-radius: 4px;
                background-color: #0d1117;
            }
        """)

        # Tags widget
        self.tags_widget = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_widget)
        self.tags_layout.setContentsMargins(4, 4, 4, 4)
        self.tags_layout.setSpacing(4)
        self.tags_layout.addStretch()

        scroll.setWidget(self.tags_widget)
        layout.addWidget(scroll)

        # Initialize with default tags
        self._refresh_tags()

    def _add_tag(self):
        """Add a new tag from input field."""
        tag = self.input_field.text().strip()
        if tag and tag not in self.tags:
            self.tags.add(tag)
            self._refresh_tags()
            self.input_field.clear()

    def _remove_tag(self, tag: str):
        """Remove a tag."""
        if tag in self.tags:
            self.tags.remove(tag)
            self._refresh_tags()

    def _refresh_tags(self):
        """Refresh the tags display."""
        # Clear existing tag widgets
        while self.tags_layout.count() > 1:  # Keep the stretch
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add tag buttons
        for tag in sorted(self.tags):
            tag_btn = QPushButton(f"{tag} ✕")
            tag_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1f6feb;
                    border: 1px solid #58a6ff;
                    border-radius: 3px;
                    padding: 3px 8px;
                    color: #ffffff;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #388bfd;
                }
            """)
            tag_btn.clicked.connect(lambda checked, t=tag: self._remove_tag(t))
            tag_btn.setCursor(Qt.PointingHandCursor)
            self.tags_layout.insertWidget(self.tags_layout.count() - 1, tag_btn)

    def get_tags(self) -> List[str]:
        """Get list of current tags."""
        return sorted(list(self.tags))


# ══════════════════════════════════════════════════════════════════════════
# PARAMETER DIALOG
# ══════════════════════════════════════════════════════════════════════════

class ParameterDialog(QDialog):
    """
    Dialog for inputting action parameters.

    Dynamically creates input widgets based on parameter schema.
    """

    def __init__(self, action_name: str, complex_param: dict, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.action_name = action_name
        self.complex_param = complex_param
        self.param_widgets = {}

        self._setup_ui()
        self._create_param_widgets()

    def _setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle(f"Parameters: {self.action_name}")
        self.setMinimumWidth(400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        # Dark theme stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #1e232d;
                color: #e6ebf5;
            }
            QLabel {
                color: #8b949e;
                font-weight: bold;
                font-size: 11px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 6px;
                color: #e6ebf5;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #58a6ff;
            }
            QCheckBox {
                color: #e6ebf5;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #30363d;
                border-radius: 3px;
                background-color: #0d1117;
            }
            QCheckBox::indicator:checked {
                background-color: #58a6ff;
                border-color: #58a6ff;
            }
            QPushButton {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e6ebf5;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #30363d;
                border-color: #58a6ff;
            }
            QPushButton:pressed {
                background-color: #161b22;
            }
            QPushButton[default="true"] {
                background-color: #1f6feb;
                border-color: #58a6ff;
            }
            QPushButton[default="true"]:hover {
                background-color: #388bfd;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Form layout for parameters
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(10)
        main_layout.addLayout(self.form_layout)

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        # Style OK button as default
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setProperty("default", "true")
        ok_button.setText("Run Action")

    def _create_param_widgets(self):
        """Create input widgets for each parameter."""
        if not self.complex_param:
            label = QLabel("This action has no configurable parameters.")
            label.setStyleSheet("color: #8b949e; font-weight: normal; font-style: italic;")
            self.form_layout.addRow(label)
            return

        for param_name, param_def in self.complex_param.items():
            widget = self._create_widget_for_param(param_name, param_def)
            if widget:
                label = QLabel(param_name)
                self.form_layout.addRow(label, widget)
                self.param_widgets[param_name] = widget

    def _create_widget_for_param(self, param_name: str, param_def) -> Optional[QWidget]:
        """Create appropriate widget based on parameter type."""
        # Extract type and value
        if isinstance(param_def, dict):
            param_type = param_def.get('type', 'text')
            default_value = param_def.get('value', '')
            choices = param_def.get('choices', [])
        else:
            param_type = 'text'
            default_value = param_def
            choices = []

        # Create widget based on type
        if param_type in ('bool', 'boolean'):
            widget = QCheckBox()
            widget.setChecked(bool(default_value))
            widget.param_type = 'bool'
            return widget

        elif param_type == 'list':
            widget = QComboBox()
            widget.addItems([str(c) for c in choices])
            if default_value:
                widget.setCurrentText(str(default_value))
            widget.param_type = 'list'
            return widget

        elif param_type == 'fixedlist':
            # Create container for multiple checkboxes
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)

            default_list = default_value if isinstance(default_value, list) else []
            checkboxes = []

            for choice in choices:
                cb = QCheckBox(str(choice))
                cb.setChecked(choice in default_list)
                layout.addWidget(cb)
                checkboxes.append(cb)

            container.checkboxes = checkboxes
            container.param_type = 'fixedlist'
            return container

        elif param_type == 'longtext':
            widget = QTextEdit()
            widget.setPlainText(str(default_value))
            widget.setMaximumHeight(100)
            widget.param_type = 'longtext'
            return widget

        elif param_type == 'tags':
            # Tags input widget
            default_tags = default_value if isinstance(default_value, list) else []
            widget = TagsInputWidget(default_tags=default_tags)
            widget.param_type = 'tags'
            return widget

        else:  # 'text', 'save', or default
            widget = QLineEdit()
            widget.setText(str(default_value))
            widget.setPlaceholderText(f"Enter {param_name}...")
            widget.param_type = 'text'
            return widget

    def get_parameters(self) -> dict:
        """Extract parameter values from widgets."""
        params = {}

        for param_name, widget in self.param_widgets.items():
            param_type = getattr(widget, 'param_type', 'text')

            if param_type == 'bool':
                params[param_name] = {'type': 'bool', 'value': widget.isChecked()}

            elif param_type == 'list':
                params[param_name] = {'type': 'list', 'value': widget.currentText()}

            elif param_type == 'fixedlist':
                selected = [cb.text() for cb in widget.checkboxes if cb.isChecked()]
                params[param_name] = {'type': 'fixedlist', 'value': selected}

            elif param_type == 'longtext':
                params[param_name] = {'type': 'longtext', 'value': widget.toPlainText()}

            elif param_type == 'tags':
                params[param_name] = {'type': 'tags', 'value': widget.get_tags()}

            else:  # text
                params[param_name] = {'type': 'text', 'value': widget.text()}

        return params

    def keyPressEvent(self, event):
        """Handle key press - Escape to cancel, Enter to accept."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter) and not isinstance(
            self.focusWidget(), QTextEdit
        ):
            self.accept()
        else:
            super().keyPressEvent(event)


# ══════════════════════════════════════════════════════════════════════════
# RECTANGLE BUTTON
# ══════════════════════════════════════════════════════════════════════════

class RectangleButton(QWidget):
    """
    A single rectangular button in the vertical menu.

    Represents one data type with associated actions.
    """

    def __init__(
        self,
        data_type: str,
        geometry: ButtonGeometry,
        parser: clipParser,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.data_type = data_type
        self.geometry = geometry
        self.parser = parser

        # State
        self.hovered = False
        self.pressed = False

        # Cache
        self._path = geometry.create_path()
        self._color = generate_type_color(data_type)
        self._actions_menu: Optional[QMenu] = None

        # Setup
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

        # Font
        self.font = QFont(Config.FONT_FAMILY, Config.FONT_SIZE, Config.FONT_WEIGHT)

    def paint(self, painter: QPainter):
        """Paint this rectangle button."""
        painter.setRenderHint(QPainter.Antialiasing)

        # Determine colors based on state
        if getattr(self, 'pressed', False):
            fill_color = self._color.darker(120)
        elif getattr(self, 'hovered', False):
            fill_color = Config.HOVER_COLOR
        else:
            fill_color = self._color

        # Draw rounded rectangle
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(Config.BORDER_COLOR, 1.5))
        painter.drawPath(self._path)

        # Draw text (left-aligned with padding)
        painter.setFont(self.font)
        painter.setPen(QPen(Config.TEXT_COLOR))

        text_rect = self.geometry.rect.adjusted(12, 0, -40, 0)  # Left padding, leave space for badge

        # Text shadow for better readability
        shadow_color = QColor(0, 0, 0, 100)
        painter.setPen(QPen(shadow_color))
        painter.drawText(text_rect.adjusted(1, 1, 1, 1), Qt.AlignVCenter | Qt.AlignLeft, self.data_type.upper())

        painter.setPen(QPen(Config.TEXT_COLOR))
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.data_type.upper())

        # Always draw count badge on the right
        count = len(self.parser.matches.get(self.data_type, []))
        if count > 0:
            badge_pos = self.geometry.badge_position()
            self._draw_count_badge(painter, badge_pos, count)

    def _draw_count_badge(self, painter: QPainter, pos: QPointF, count: int):
        """Draw a small badge showing the count of items."""
        badge_text = str(count)
        fm = QFontMetrics(self.font)
        badge_width = max(fm.horizontalAdvance(badge_text) + 10, 24)
        badge_height = 18

        badge_rect = QRectF(
            pos.x() - badge_width / 2,
            pos.y() - badge_height / 2,
            badge_width,
            badge_height
        )

        # Badge background
        painter.setBrush(QBrush(QColor(45, 55, 70, 220)))
        painter.setPen(QPen(Config.BORDER_COLOR, 1))
        painter.drawRoundedRect(badge_rect, 9, 9)

        # Badge text
        painter.setPen(QPen(Config.TEXT_COLOR))
        painter.drawText(badge_rect, Qt.AlignCenter, badge_text)

    def contains_point(self, point: QPoint) -> bool:
        """Check if point is inside this wedge."""
        return self._path.contains(QPointF(point))

    def handle_left_click(self):
        """Handle left click - copy items to clipboard."""
        items = self.parser.matches.get(self.data_type, [])
        if items:
            text = "\r\n".join(str(item) for item in items)
            pyperclip.copy(text)
            async_toast(f"✓ Copied {len(items)} {self.data_type.upper()} item(s)")

    def handle_right_click(self, global_pos: QPoint):
        """Handle right click - show actions menu."""
        valid_actions = self._get_valid_actions()

        if not valid_actions:
            async_toast(f"No actions available for {self.data_type}")
            return

        # Create and show menu
        if self._actions_menu:
            self._actions_menu.deleteLater()

        self._actions_menu = QMenu()
        self._actions_menu.setStyleSheet("""
            QMenu {
                background-color: #1e232d;
                border: 1px solid #646e82;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                color: #e6ebf5;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #58a6ff;
            }
        """)

        for action_name, action in valid_actions:
            self._actions_menu.addAction(
                action_name,
                partial(self._execute_action, action_name)
            )

        self._actions_menu.exec_(global_pos)

    def _get_valid_actions(self) -> List[Tuple[str, object]]:
        """Get list of valid actions for this data type."""
        valid_actions = []
        for action_name, action in self.parser.actions.items():
            if self.data_type in getattr(action, 'supportedType', []):
                valid_actions.append((action_name, action))
        return sorted(valid_actions, key=lambda x: x[0])

    def _execute_action(self, action_name: str):
        """Execute an action and copy results to clipboard."""
        action = self.parser.actions.get(action_name)
        if not action:
            async_toast(f"⚠ Action {action_name} not found")
            return

        # Check if action has parameters
        complex_param = getattr(action, 'complex_param', {})

        if complex_param and isinstance(complex_param, dict) and complex_param:
            # Show parameter dialog
            param_dialog = ParameterDialog(action_name, complex_param, self.parent())

            if param_dialog.exec_() != QDialog.Accepted:
                return  # User cancelled

            # Get parameters and update action
            params = param_dialog.get_parameters()
            action.complex_param = params

        # Execute action
        try:
            result = str(action)
            pyperclip.copy(result)
            async_toast(f"✓ {action_name.upper()} results copied")
        except Exception as e:
            async_toast(f"⚠ Error executing {action_name}: {str(e)}")
            return

        # Close menu
        if self.parent():
            self.parent().close()


# ══════════════════════════════════════════════════════════════════════════
# VERTICAL MENU
# ══════════════════════════════════════════════════════════════════════════

class VerticalMenu(QWidget):
    """
    Main vertical menu widget.

    Displays parsed clipboard data types in a vertical list of rectangular buttons.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Window setup
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # State - use global singleton parser
        self.parser = get_parser()
        self.buttons: List[RectangleButton] = []
        self.hovered_button: Optional[RectangleButton] = None

        # Animation
        self._opacity = 0.0
        self._scale = 0.95
        self._setup_animations()

        # Mouse tracking
        self.setMouseTracking(True)

        # Enable keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)

    def _setup_animations(self):
        """Setup show/hide animations."""
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(Config.FADE_DURATION)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(Config.SCALE_DURATION)
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)

    @pyqtProperty(float)
    def opacity(self) -> float:
        """Opacity property for animation."""
        return self._opacity

    @opacity.setter
    def opacity(self, value: float):
        self._opacity = value
        self.update()

    @pyqtProperty(float)
    def scale(self) -> float:
        """Scale property for animation."""
        return self._scale

    @scale.setter
    def scale(self, value: float):
        self._scale = value
        self.update()

    def show_at_position(self, pos: QPoint):
        """Show menu at given position with animation."""
        # Parse clipboard
        try:
            clipboard_text = pyperclip.paste()
            if not clipboard_text:
                async_toast("⚠ Clipboard is empty")
                return

            print(f"[DEBUG] Clipboard text length: {len(clipboard_text)}")
            print(f"[DEBUG] Parsers loaded: {len(self.parser.parsers)}")
            print(f"[DEBUG] Actions loaded: {len(self.parser.actions)}")

            self.parser.parseData(clipboard_text)
            detected_types = list(self.parser.detectedType)

            print(f"[DEBUG] Detected types: {detected_types}")
            print(f"[DEBUG] Matches: {self.parser.matches}")

            if len(detected_types) < Config.MIN_BUTTONS:
                async_toast(f"⚠ No parseable data found in clipboard (parsers: {len(self.parser.parsers)})")
                return

            if len(detected_types) > Config.MAX_BUTTONS:
                detected_types = detected_types[:Config.MAX_BUTTONS]
                async_toast(f"⚠ Showing first {Config.MAX_BUTTONS} types")

            # Sort alphabetically
            detected_types.sort()

        except Exception as e:
            async_toast(f"⚠ Error parsing clipboard: {e}")
            return

        # Create buttons
        self._create_buttons(detected_types)

        # Calculate menu size based on number of buttons
        menu_width = Config.BUTTON_WIDTH + 2 * Config.MENU_PADDING
        menu_height = (len(detected_types) * Config.BUTTON_HEIGHT +
                      (len(detected_types) - 1) * Config.BUTTON_SPACING +
                      2 * Config.MENU_PADDING)
        self.setFixedSize(menu_width, menu_height)

        # Position menu near cursor (offset to avoid cursor being over menu)
        self.move(pos + QPoint(10, 10))

        # Animate in
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.scale_animation.setStartValue(0.95)
        self.scale_animation.setEndValue(1.0)

        super().show()
        self.fade_animation.start()
        self.scale_animation.start()

        # Set focus to receive keyboard events
        self.setFocus()
        self.activateWindow()

    def _create_buttons(self, data_types: List[str]):
        """Create rectangular buttons for detected types."""
        self.buttons.clear()

        for i, data_type in enumerate(data_types):
            y_pos = Config.MENU_PADDING + i * (Config.BUTTON_HEIGHT + Config.BUTTON_SPACING)

            rect = QRectF(
                Config.MENU_PADDING,
                y_pos,
                Config.BUTTON_WIDTH,
                Config.BUTTON_HEIGHT
            )

            geometry = ButtonGeometry(rect=rect)
            button = RectangleButton(data_type, geometry, self.parser, self)
            self.buttons.append(button)

    def paintEvent(self, event):
        """Paint the menu background and buttons."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Apply opacity for fade animation
        painter.setOpacity(self._opacity)

        # Apply scale transform
        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        painter.translate(center)
        painter.scale(self._scale, self._scale)
        painter.translate(-center)

        # Draw rounded background container
        background_rect = QRectF(0, 0, self.width(), self.height())
        painter.setBrush(QBrush(Config.BG_COLOR))
        painter.setPen(QPen(Config.BORDER_COLOR, 2))
        painter.drawRoundedRect(background_rect, 8, 8)

        # Draw buttons
        for button in self.buttons:
            button.paint(painter)

    def mouseMoveEvent(self, event):
        """Track mouse movement for hover effects."""
        pos = event.pos()
        prev_hovered = self.hovered_button
        self.hovered_button = None

        # Find hovered button
        for button in self.buttons:
            if button.contains_point(pos):
                self.hovered_button = button
                button.hovered = True
            else:
                button.hovered = False

        # Update if hover changed
        if prev_hovered != self.hovered_button:
            self.update()

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if self.hovered_button and hasattr(self.hovered_button, 'pressed'):
            self.hovered_button.pressed = True
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if not self.hovered_button:
            return

        try:
            if event.button() == Qt.LeftButton:
                self.hovered_button.handle_left_click()
                self.close()
            elif event.button() == Qt.RightButton:
                self.hovered_button.handle_right_click(event.globalPos())
        finally:
            # Always reset pressed state
            if self.hovered_button:
                self.hovered_button.pressed = False
            self.update()

    def leaveEvent(self, event):
        """Handle mouse leaving widget."""
        # Reset all button states
        for button in self.buttons:
            button.hovered = False
            button.pressed = False

        self.hovered_button = None
        self.update()

    def keyPressEvent(self, event):
        """Handle key press - Escape to close."""
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Animate out before closing."""
        self.fade_animation.setStartValue(self._opacity)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

        # Actually close after animation
        super().closeEvent(event)


# ══════════════════════════════════════════════════════════════════════════
# GLOBAL SHORTCUT HANDLER
# ══════════════════════════════════════════════════════════════════════════

class SafeTriggerEvent(QEvent):
    """Custom event for thread-safe menu triggering."""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self):
        super().__init__(self.EVENT_TYPE)


class VerticalCyberClip(QWidget):
    """
    Main application widget for CyberClip vertical menu.

    Manages global keyboard shortcut and menu lifecycle.
    """

    def __init__(self):
        super().__init__()

        # Hidden main window
        self.setWindowTitle("CyberClip Vertical Menu")
        self.setGeometry(0, 0, 1, 1)
        self.hide()

        # Vertical menu
        self.vertical_menu = VerticalMenu()

        # Register global shortcut in separate thread
        threading.Thread(target=self._register_shortcut, daemon=True).start()

    def _register_shortcut(self):
        """Register global keyboard shortcut."""
        try:
            keyboard.add_hotkey(
                Config.KEYBOARD_SHORTCUT,
                self._safe_trigger_menu
            )
        except Exception as e:
            print(f"Failed to register shortcut: {e}")

    def _safe_trigger_menu(self):
        """Post event to trigger menu from shortcut thread."""
        QCoreApplication.postEvent(self, SafeTriggerEvent())

    def _trigger_menu(self):
        """Actually trigger the menu (main thread)."""
        cursor_pos = QApplication.desktop().cursor().pos()
        self.vertical_menu.show_at_position(cursor_pos)

    def customEvent(self, event):
        """Handle custom events."""
        if event.type() == SafeTriggerEvent.EVENT_TYPE:
            self._trigger_menu()


# ══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point."""
    # Check for required dependencies
    if _MISSING_DEPS:
        print("❌ CyberClip Menu requires additional dependencies.")
        print(f"   Missing: {', '.join(_MISSING_DEPS)}")
        print("\nTo install GUI dependencies with uv (recommended):")
        print('   uv tool install "git+https://github.com/BongoKnight/cyberclip[gui]"')
        print("\nOr with pip:")
        print("   pip install cyberclip[gui]")
        print("\nFor all optional dependencies:")
        print('   uv tool install "git+https://github.com/BongoKnight/cyberclip[all]"')
        print("   # or: pip install cyberclip[all]")
        sys.exit(1)

    if not _TOAST_AVAILABLE:
        print("⚠ win11toast not available - using console notifications")

    # Preload parser before creating Qt application
    print("📡 Loading parsers and actions...")
    parser = get_parser()
    print(f"✓ Loaded {len(parser.parsers)} parsers and {len(parser.actions)} actions")

    app = QApplication(sys.argv)
    app.setApplicationName("CyberClip Menu")

    # Create and show main widget
    widget = VerticalCyberClip()

    print(f"✓ CyberClip Menu started")
    print(f"✓ Press {Config.KEYBOARD_SHORTCUT.upper()} to open menu")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
