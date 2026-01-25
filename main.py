import flet as ft
from timer_logic import PomodoroTimer
import os

def main(page: ft.Page):
    page.title = "Pomodoro Timer"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 500
    page.window_resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # Audio for alarm
    # Ensure you have an 'alarm.mp3' in assets or update the path.
    # For now, we will add the Audio control but it might not play if file is missing.
    alarm_audio = ft.Audio(src="assets/alarm.mp3", autoplay=False)
    page.overlay.append(alarm_audio)

    # State
    timer = None

    # UI Components
    task_input = ft.TextField(
        hint_text="What are you working on?",
        text_align=ft.TextAlign.CENTER,
        border=ft.InputBorder.UNDERLINE,
        width=300
    )

    timer_text = ft.Text(
        value="25:00",
        size=80,
        weight=ft.FontWeight.BOLD,
        color="white"
    )

    status_text = ft.Text(
        value="Work",
        size=20,
        color="grey"
    )

    def on_timer_update(time_str):
        timer_text.value = time_str
        page.update()

    def advance_mode():
        new_mode = timer.switch_mode()
        status_text.value = new_mode
        start_button.text = "Start"
        start_button.icon = "play_arrow"
        page.update()

    def on_timer_complete():
        # Play sound
        # active_audio.play() # Uncomment if file exists
        page.snack_bar = ft.SnackBar(ft.Text("Time's up! Take a break!"))
        page.snack_bar.open = True

        # Native notification
        try:
            from plyer import notification
            notification.notify(
                title="Pomodoro Timer",
                message="Time's up! Take a break!",
                app_name="Pomodoro",
                timeout=10
            )
        except ImportError:
            print("Plyer not installed, skipping notification")
        except Exception as e:
            print(f"Notification error: {e}")

        advance_mode()

    # Initialize Logic
    timer = PomodoroTimer(on_timer_update, on_timer_complete)

    def start_timer(e):
        if not timer.is_running:
            timer.start()
            start_button.text = "Pause"
            start_button.icon = "pause"
            page.update()
        else:
            timer.pause()
            start_button.text = "Start"
            start_button.icon = "play_arrow"
            page.update()

    def reset_timer(e):
        timer.reset()
        start_button.text = "Start"
        start_button.icon = "play_arrow"
        page.update()

    def switch_mode(e):
        advance_mode()

    start_button = ft.ElevatedButton(
        text="Start",
        icon="play_arrow",
        on_click=start_timer,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=20
        )
    )

    reset_button = ft.IconButton(
        icon="refresh",
        on_click=reset_timer,
        tooltip="Reset Timer"
    )

    mode_button = ft.IconButton(
        icon="swap_horiz",
        on_click=switch_mode,
        tooltip="Switch Mode (Work/Break)"
    )

    # Settings Components
    work_input = ft.TextField(label="Work (min)", value="25", width=100)
    break_input = ft.TextField(label="Break (min)", value="5", width=100)

    def close_dlg(e):
        page.close(settings_dialog)

    def save_settings(e):
        try:
            w = int(work_input.value)
            b = int(break_input.value)
            timer.set_duration(w, b)
            page.close(settings_dialog)
            page.snack_bar = ft.SnackBar(ft.Text("Settings saved!"))
            page.snack_bar.open = True
            page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter valid numbers"))
            page.snack_bar.open = True
            page.update()

    settings_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Settings"),
        content=ft.Row([work_input, break_input]),
        actions=[
            ft.TextButton("Cancel", on_click=close_dlg),
            ft.TextButton("Save", on_click=save_settings),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_settings(e):
        page.open(settings_dialog)

    # Layout
    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(icon="settings", on_click=open_settings, tooltip="Settings")
                    ],
                    alignment=ft.MainAxisAlignment.END
                ),
                task_input,
                ft.Container(height=20),
                status_text,
                timer_text,
                ft.Container(height=20),
                ft.Row(
                    [mode_button, start_button, reset_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
