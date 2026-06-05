"""Переиспользуемые виджеты интерфейса."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def make_scrollable(content: QWidget) -> QScrollArea:
    """Оборачивает виджет в прокручиваемую область."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setWidget(content)
    return scroll


def make_section_title(text: str) -> QLabel:
    """Создаёт заголовок секции с единым стилем."""
    label = QLabel(text)
    label.setObjectName("sectionTitle")
    return label


def make_hint_label(text: str) -> QLabel:
    """Создаёт подсказку с приглушённым стилем."""
    label = QLabel(text)
    label.setObjectName("hintLabel")
    label.setWordWrap(True)
    return label


def make_labeled_input(
    label_text: str,
    placeholder: str = "",
    password: bool = False,
) -> tuple[QLabel, QLineEdit]:
    """Создаёт пару метка + поле ввода."""
    label = QLabel(label_text)
    field = QLineEdit()
    field.setPlaceholderText(placeholder)

    if password:
        field.setEchoMode(QLineEdit.EchoMode.Password)

    return label, field


def make_form_row(label: QLabel, field: QWidget) -> QWidget:
    """Создаёт горизонтальную строку формы."""
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    label.setMinimumWidth(180)
    layout.addWidget(label)
    layout.addWidget(field, stretch=1)
    return row


def make_button_row(*buttons: QPushButton) -> QHBoxLayout:
    """Создаёт горизонтальный ряд кнопок с выравниванием вправо."""
    layout = QHBoxLayout()
    layout.addStretch()

    for button in buttons:
        layout.addWidget(button)

    return layout


def populate_form(
    layout: QFormLayout,
    fields: dict[str, QLineEdit],
    labels: dict[str, str],
) -> None:
    """Добавляет поля ввода в форму по словарю меток."""
    for key, label_text in labels.items():
        layout.addRow(label_text, fields[key])
