import os
from plover.gui_qt.tool import Tool
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGroupBox,
    QRadioButton,
    QTextEdit,
    QPushButton,
    QMessageBox
)
from plover.resource import resource_exists, resource_filename
from plover.oslayer.config import CONFIG_DIR
import ast

class PloverSoundConfig(Tool):
    TITLE = 'Sound'
    ICON = 'asset:plover_sound:icon.svg'
    ROLE = 'plover_sound'

    def __init__(self, engine):
        super().__init__(engine)
        self.engine = engine
        layout = QVBoxLayout(self)
        if 'play_sound' in self.engine.config['enabled_extensions']:
            self.config_file_path = os.path.join(CONFIG_DIR, "plover_sound_conf.py")

            # Open the configuration file and check for existing settings
            self.load_config()


            # Add radio buttons
            mode_group = QGroupBox("Modes", parent=self)
            mode_layout = QVBoxLayout(mode_group)
            self.radio_button_1 = QRadioButton("Mapped", parent=mode_group)
            self.radio_button_2 = QRadioButton("Melody", parent=mode_group)
            self.radio_button_3 = QRadioButton("Sample", parent=mode_group)
            mode_layout.addWidget(self.radio_button_1)
            mode_layout.addWidget(self.radio_button_2)
            mode_layout.addWidget(self.radio_button_3)
            layout.addWidget(mode_group)

            # Add text area
            self.text_area = QTextEdit(self)
            layout.addWidget(self.text_area)

            # Set initial radio button and text area values
            self.set_initial_values()

            # Add save button
            save_button = QPushButton("Save", parent=self)
            save_button.clicked.connect(self.save_config)
            layout.addWidget(save_button)
        else:
            # Display message explaining how to enable plover-sound extension
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Plover Sound Extension")
            message_box.setText("The Plover Sound extension is not enabled.")
            message_box.setInformativeText("To enable it, go to Plover's configuration menu under the 'Plugins' tab and select the box next to play_sound.")

            # Connect OK button click event to close the layout's window
            message_box.buttonClicked.connect(self.window().close)

            layout.addWidget(message_box)



    def load_config(self):
        # Check if configuration file exists
        try:
            with open(self.config_file_path, 'r') as config_file:
                config_content = config_file.read()
                config_dict = ast.literal_eval(config_content)
        except FileNotFoundError:
            # Configuration file doesn't exist, create with default values
            config_dict = {
                'mode': default_mode,
                'melody_notes': default_melody_notes,
                'note_map': default_note_map,
                'sample_path': default_sample_path
            }
            with open(self.config_file_path, 'w') as config_file:
                config_file.write(str(config_dict))

        except SyntaxError:
            raise Exception("Invalid syntax in plover_sound config")
            return
        return config_dict

    def set_initial_values(self):
        config_dict = self.load_config()
        # Set radio button
        if config_dict['mode'] == 'mapped':
            self.radio_button_1.setChecked(True)
        elif config_dict['mode'] == 'melody':
            self.radio_button_2.setChecked(True)
        elif config_dict['mode'] == 'sample':
            self.radio_button_3.setChecked(True)
        # Populate text area
        text_content = "Melody Notes:\n{}\n\nNote Map:\n{}\n\nSample Path:\n{}".format(
            '\n'.join(config_dict['melody_notes']),
            '\n'.join(["{}: {}".format(key, value) for key, value in config_dict['note_map'].items()]),
            config_dict['sample_path']
        )
        self.text_area.setPlainText(text_content)

    def save_config(self):
        # Get values from radio buttons and text area
        if self.radio_button_1.isChecked():
            mode = 'mapped'
        elif self.radio_button_2.isChecked():
            mode = 'melody'
        elif self.radio_button_3.isChecked():
            mode = 'sample'
        config_text = self.text_area.toPlainText()
        melody_notes = []
        note_map = {}
        sample_path = ""
        # Parse text area content to extract configuration settings
        lines = config_text.split('\n')
        section = None
        for line in lines:
            if line == "Melody Notes:":
                section = 'melody_notes'
            elif line == "Note Map:":
                section = 'note_map'
            elif line == "Sample Path:":
                section = 'sample_path'
            elif section == 'melody_notes':
                melody_notes.append(line.strip())
            elif section == 'note_map':
                if ':' in line:
                    key, value = line.split(':', 1)  # Split at most once
                    note_map[key.strip()] = value.strip()
            elif section == 'sample_path':
                sample_path = line.strip()
        config_dict = {
            'mode': mode,
            'melody_notes': melody_notes,
            'note_map': note_map,
            'sample_path': sample_path
        }
        # Write updated configuration to file
        with open(self.config_file_path, 'w') as config_file:
            config_file.write(str(config_dict))

        # Show system message for successful save
        QMessageBox.information(self, "Success", "Configuration saved successfully.")

        # Restart steno engine
        self.engine.restart()
