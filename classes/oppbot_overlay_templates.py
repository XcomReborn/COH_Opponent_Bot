class OverlayTemplates:
    "Templates for HTML and CSS output files."

    overlayhtml = """
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" type="text/css" href="{}">
<meta http-equiv="content-type" content="text-html; charset=utf-8">
    <script>
        var previousDate;
        var backgroundScript = setInterval(checkIfFileHasChanged, 5000);

        function checkIfFileHasChanged() {{
            date = new Date(window.location.pathname.lastModified);
            if (previousDate != null) {{
                if (date.getTime() !== previousDate.getTime()) {{
                    window.location.reload();
                }}
            }}
            previousDate = date;
        }}
    </script>
</head>
<body>
<div class="container">
<div class = "playerTeam">
{}
</div>
<div class = "opponentTeam">
{}
</div>
</div>
<div style="clear: both;"></div>
</body>
</html>
"""

    statshtml = """
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" type="text/css" href="{}">
<meta http-equiv="content-type" content="text-html; charset=utf-8">
    <script>
        var previousDate;
        var backgroundScript = setInterval(checkIfFileHasChanged, 5000);

        function checkIfFileHasChanged() {{
            date = new Date(window.location.pathname.lastModified);
            if (previousDate != null) {{
                if (date.getTime() !== previousDate.getTime()) {{
                    window.location.reload();
                }}
            }}
            previousDate = date;
        }}
    </script>
</head>
<body>
<div class="container">
<div class = "playerStats">
{}
</div>
</div>
<div style="clear: both;"></div>
</body>
</html>
"""

    overlaycss = """


body {
    position: relative;
    background-color: transparent;
    padding: 0pt;

  }

html {
    position: relative;
    padding: 0pt;
}

.container{width:100%;
    position: relative;
    top: 0pt;
    font-size: 14pt;
}

.countryflagimg{
    position: relative;
    display: inline;
    height: 16pt;
    top: 0pt;
}

.countryflagimg img{
    position: relative;
    display: inline;
    height:16pt;
    top: -3pt;
}


.factionflagimg{
    position: relative;
    display: inline;
    height: 16pt;
    top: 0pt;
}

.factionflagimg img{
    position: relative;
    height:18pt;
    top: -3pt;
}

.rankimg {
    position: relative;
    top: 10pt;
    height: 30pt;
    display: inline;
}

.rankimg img{
    position: relative;
    height: 24pt;
    display: inline;
    top: -8pt;
}

.textVariables {
    position: relative;
    display: inline;
    top: -6pt;
}

.name {
    position: relative;
    display: inline;
    top: 0pt;
}

.faction {
    position: relative;
    display: inline;
    top: 0pt;
}

.matchtype {
    position: relative;
    display: inline;
    top: 0pt;
}

.country {
    position: relative;
    display: inline;
    top: 0pt;
}

.totalwins {
    position: relative;
    display: inline;
    top: 0pt;
}

.totallosses {
    position: relative;
    display: inline;
    top: 0pt;
}

.totalwlratio {
    position: relative;
    display: inline;
    top: 0pt;
}

.wins {
    position: relative;
    display: inline;
    top: 0pt;
}

.losses {
    position: relative;
    display: inline;
    top: 0pt;
}

.disputes {
    position: relative;
    display: inline;
    top: 0pt;
}

.streak {
    position: relative;
    display: inline;
    top: 0pt;
}

.drops {
    position: relative;
    display: inline;
    top: 0pt;
}

.rank {
    position: relative;
    display: inline;
    top: 0pt;
}

.level {
    position: relative;
    display: inline;
    top: 0pt;
}

.wlratio {
    position: relative;
    display: inline;
    top: 0pt;
}

.nonVariableText{
    position: relative;
    display: inline;
    top: -6pt;
}

.steamprofile{
    position: relative;
    display: inline;
    top: 0pt;
}

.cohstatslink{
position: relative;
display: inline;
top: 0pt;
}

.steamid {
    position: relative;
    display: inline;
    top: 0pt;
}

.opponentTeam {

      position : absolute;
      top: 3pt;
      background-color: rgba(0, 0, 0, 0.5);
      color: white;
      float: left;
      margin-left: 58%;
      text-align: left;
      padding-bottom: 0pt;
      }

.opponentTeam .name{

color: white;

}

.playerTeam {

      position: relative;
      top: 2pt;
      background-color: rgba(0, 0, 0, 0.5);
      color: white;
      float: right;
      margin-right: 58%;
      text-align: right;
      padding-bottom: 0pt;

  }

  .playerTeam .name{

    color: white;

}

.playerStats {

      position: relative;
      top: 0pt;
      background-color: rgba(0, 0, 0, 0.5);
      color: white;
      float: right;
      margin-right: 58%;
      text-align: right;
      padding-bottom: 0pt;

  }

.US{
}
.WM{
}
.PE{
}
.CW{
}

.CUSTOM{
}
.ONES{
}
.TWOS{
}
.THREES{
}
.FOURS{
} 
.TEAM_2v2{
}
.TEAM_3V3 {
}
.TEAM_4V4 {
}
.ASSAULT_2V2 {
}
.ASSAULT_TEAM_2V2 {
}
.ASSAULT_TEAM_3V3 {
}
.PANZERKRIEG_2v2 {
}
.PANZERKRIEG_TEAM_2v2 {
}
.PANZERKRIEG_TEAM_3v3 {
}
.COMPSTOMP {
}
.ASSAULT {
}
.PANZERKRIEG {
}
.STONEWALL {
} 

/* players 1-4 will always be on the player team */
.player1 {
}
.player2 {
}
.player3 {
}
.player4 {
}

/* players 5-8 will always be on the opponent team */
.player5 {
}
.player6 {
}
.player7 {
}
.player8 {
}

    """
