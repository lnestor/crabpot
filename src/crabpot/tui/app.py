import textual.app
import textual.widgets

class CrabpotApp(textual.app.App):
    def compose(self):
        yield textual.widgets.Header()
        yield textual.widgets.Footer()

