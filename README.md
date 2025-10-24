The Following Json will be generated on first start:

{
    "width": 1920,
    "height": 80,
    "font_size": 24,
    "font_color": "#FFFFFF",
    "bg_color": "#000000",
    "font_family": "Arial",
    "scroll_speed": 10,
    "step": 1,
    "feeds": [
        "https://www.espn.com/espn/rss/news"
    ]
}

These are the settings you can change on the built version.

Width is in pixels. I recommend setting to the width of your display

Height is in pixels. Scale as desired 80 is small but good for desktop setting.

Font size is in point.

Font Color is in RGB. Most photo editing apps can supply this or a color picker online

Background color is also in RGB

Font Family some choices can be found here: https://stackoverflow.com/questions/39614027/list-available-font-families-in-tkinter

Scroll Speed is in ms: After X ms then the step will be applied moving the text the number of step pixels left. This loops indefinitely.

Step is in pixels and is the number of pixels the text will move left after the scroll interval and looping indefinitely.

Feeds is a comma separated list of rss feed urls. Careful on this part if the app crashes this is likely missing a comma or misformatted
Enters and spaces are fine.

Example of some:
[
             "https://www.mlb.com/mariners/feeds/news/rss.xml",
             "https://www.espn.com/espn/rss/news",
             "https://www.espn.com/espn/rss/mlb/news",
             "https://www.pff.com/feed/teams/29",
             "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
             "https://www.espn.com/espn/rss/nfl/news",
             "https://soundofhockey.com/feed/",
             "https://www.mlb.com/feeds/news/rss.xml",
             "https://www.espn.com/espn/rss/soccer/news",
             "https://www.nytimes.com/athletic/rss/nfl/",
             "https://www.espn.com/espn/rss/ncaa/news",
             "https://www.espn.com/espn/rss/ncf/news",
             "https://www.ncaa.com/news/football/fbs/rss.xml",
             "https://www.ncaa.com/news/soccer-men/d1/rss.xml",
             "https://www.ncaa.com/news/ncaa/d1/rss.xml",
             "https://www.espn.com/espn/rss/nhl/news"
]