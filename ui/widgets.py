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
    content.setObjectName("scrollContent")
    content.setAutoFillBackground(True)

    scroll = QScrollArea()
    scroll.setObjectName("contentScrollArea")
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setWidget(content)
    return scroll


def make_section_card(title: str) -> tuple[QWidget, QVBoxLayout]:
    """
    Создаёт карточку секции с заголовком без артефактов QGroupBox.

    Returns:
        Кортеж (карточка, layout для содержимого секции).
    """
    card = QWidget()
    card.setObjectName("sectionCard")

    outer = QVBoxLayout(card)
    outer.setContentsMargins(20, 18, 20, 20)
    outer.setSpacing(12)

    title_label = QLabel(title)
    title_label.setObjectName("sectionCardTitle")
    outer.addWidget(title_label)

    body_layout = QVBoxLayout()
    body_layout.setContentsMargins(0, 0, 0, 0)
    body_layout.setSpacing(10)
    outer.addLayout(body_layout)

    return card, body_layout


def make_section_title(text: str) -> QLabel:
    """Создаёт заголовок страницы с единым стилем."""
    label = QLabel(text)
    label.setObjectName("sectionTitle")
    return label


def make_form_label(text: str) -> QLabel:
    """Создаёт метку поля формы с единым стилем."""
    label = QLabel(text)
    label.setObjectName("formLabel")
    return label


def make_hint_label(text: str) -> QLabel:
    """Создаёт подсказку с приглушённым стилем."""
    label = QLabel(text)
    label.setObjectName("hintLabel")
    label.setWordWrap(True)
    return label


def make_credit_label(text: str) -> QLabel:
    """Создаёт метку с информацией об авторе."""
    label = QLabel(text)
    label.setObjectName("creditLabel")
    return label


def make_labeled_input(
    label_text: str,
    placeholder: str = "",
    password: bool = False,
) -> tuple[QLabel, QLineEdit]:
    """Создаёт пару метка + поле ввода."""
    label = QLabel(label_text)
    label.setObjectName("formLabel")
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
    layout.setSpacing(10)
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
        label = QLabel(label_text)
        label.setObjectName("formLabel")
        layout.addRow(label, fields[key])
