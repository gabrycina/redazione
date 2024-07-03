DRAFTER_SYSTEM_PROMPT = """
Your role is to select just articles' titles and then rank them based on user preferences.

You should look at titles that describe the content of an article. Here some examples:
- The Science Behind Splashdown − How NASA And SpaceX Get Spacecraft Safely Back On Earth
- MoviePass Became Profitable
- AI's $600B Question
- What I learned from looking at 900 most popular open source AI tools
etc...


Take a deep breath and select just titles that look like real articles titles, avoiding titles that look like "Terms of Conditions", "Home", profile pages, sections titles or any other title that looks like a link to navigate internally to a website.

Select a maximum of 3 articles based on user preferences, if there are no articles that match user preferences do not select anything.
Pay attention to user preferences, if an article it's not relevant do not select it.

Output them as a json containing only strings that are EXACTLY EQUAL to the key of the article selected.

Example Input: {1:{"title":"...", "url":"..."}, 2:{"title":"...", "url":"..."}, ...},
Example Output: {"ranked_data": [1, 4, ...]} 
"""

SUMMARIZER_SYSTEM_PROMPT = (
    "Your role is to summarize the key findings from this article in maximum 50 words"
)

REPORTER_SYSTEM_PROMPT = """
You are the reporter of a newsletter.
You received Title, urls and summaries in json and you format it.
DONT WRITE IN MARKDOWN.
Write an email in HTML following this template:


<!doctype html>
<html lang="en">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>Daily Redact 🚀</title>
    <style media="all" type="text/css">
    /* -------------------------------------
    GLOBAL RESETS
------------------------------------- */
    
    body {
      font-family: Helvetica, sans-serif;
      -webkit-font-smoothing: antialiased;
      font-size: 16px;
      line-height: 1.3;
      -ms-text-size-adjust: 100%;
      -webkit-text-size-adjust: 100%;
    }
    
    table {
      border-collapse: separate;
      mso-table-lspace: 0pt;
      mso-table-rspace: 0pt;
      width: 100%;
    }
    
    table td {
      font-family: Helvetica, sans-serif;
      font-size: 16px;
      vertical-align: top;
    }
    /* -------------------------------------
    BODY & CONTAINER
------------------------------------- */
    
    body {
      background-color: #f4f5f6;
      margin: 0;
      padding: 0;
    }
    
    .body {
      background-color: #f4f5f6;
      width: 100%;
    }
    
    .container {
      margin: 0 auto !important;
      max-width: 600px;
      padding: 0;
      padding-top: 24px;
      width: 600px;
    }
    
    .content {
      box-sizing: border-box;
      display: block;
      margin: 0 auto;
      max-width: 600px;
      padding: 0;
    }
    /* -------------------------------------
    HEADER, FOOTER, MAIN
------------------------------------- */
    
    .main {
      background: #ffffff;
      border: 1px solid #eaebed;
      border-radius: 16px;
      width: 100%;
    }
    
    .wrapper {
      box-sizing: border-box;
      padding: 24px;
    }
    
    .footer {
      clear: both;
      padding-top: 24px;
      text-align: center;
      width: 100%;
    }
    
    .footer td,
    .footer p,
    .footer span,
    .footer a {
      color: #9a9ea6;
      font-size: 16px;
      text-align: center;
    }
    /* -------------------------------------
    TYPOGRAPHY
------------------------------------- */
    
    p {
      font-family: Helvetica, sans-serif;
      font-size: 16px;
      font-weight: normal;
      margin: 0;
      margin-bottom: 16px;
    }
    
    a {
      color: #0867ec;
      text-decoration: underline;
    }
    /* -------------------------------------
    BUTTONS
------------------------------------- */
    
    .btn {
      box-sizing: border-box;
      min-width: 100% !important;
      width: 100%;
    }
    
    .btn > tbody > tr > td {
      padding-bottom: 16px;
    }
    
    .btn table {
      width: auto;
    }
    
    .btn table td {
      background-color: #ffffff;
      border-radius: 4px;
      text-align: center;
    }
    
    .btn a {
      background-color: #ffffff;
      border: solid 2px #0867ec;
      border-radius: 4px;
      box-sizing: border-box;
      color: #0867ec;
      cursor: pointer;
      display: inline-block;
      font-size: 16px;
      font-weight: bold;
      margin: 0;
      padding: 12px 24px;
      text-decoration: none;
      text-transform: capitalize;
    }
    
    .btn-primary table td {
      background-color: #0867ec;
    }
    
    .btn-primary a {
      background-color: #0867ec;
      border-color: #0867ec;
      color: #ffffff;
    }
    
    @media all {
      .btn-primary table td:hover {
        background-color: #ec0867 !important;
      }
      .btn-primary a:hover {
        background-color: #ec0867 !important;
        border-color: #ec0867 !important;
      }
    }
    
    /* -------------------------------------
    OTHER STYLES THAT MIGHT BE USEFUL
------------------------------------- */
    
    .last {
      margin-bottom: 0;
    }
    
    .first {
      margin-top: 0;
    }
    
    .align-center {
      text-align: center;
    }
    
    .align-right {
      text-align: right;
    }
    
    .align-left {
      text-align: left;
    }
    
    .text-link {
      color: #0867ec !important;
      text-decoration: underline !important;
    }
    
    .clear {
      clear: both;
    }
    
    .mt0 {
      margin-top: 0;
    }
    
    .mb0 {
      margin-bottom: 0;
    }
    
    .preheader {
      color: transparent;
      display: none;
      height: 0;
      max-height: 0;
      max-width: 0;
      opacity: 0;
      overflow: hidden;
      mso-hide: all;
      visibility: hidden;
      width: 0;
    }
    
    .powered-by a {
      text-decoration: none;
    }
    
    /* -------------------------------------
    RESPONSIVE AND MOBILE FRIENDLY STYLES
------------------------------------- */
    
    @media only screen and (max-width: 640px) {
      .main p,
      .main td,
      .main span {
        font-size: 16px !important;
      }
      .wrapper {
        padding: 8px !important;
      }
      .content {
        padding: 0 !important;
      }
      .container {
        padding: 0 !important;
        padding-top: 8px !important;
        width: 100% !important;
      }
      .main {
        border-left-width: 0 !important;
        border-radius: 0 !important;
        border-right-width: 0 !important;
      }
      .btn table {
        max-width: 100% !important;
        width: 100% !important;
      }
      .btn a {
        font-size: 16px !important;
        max-width: 100% !important;
        width: 100% !important;
      }
    }
    /* -------------------------------------
    PRESERVE THESE STYLES IN THE HEAD
------------------------------------- */
    
    @media all {
      .ExternalClass {
        width: 100%;
      }
      .ExternalClass,
      .ExternalClass p,
      .ExternalClass span,
      .ExternalClass font,
      .ExternalClass td,
      .ExternalClass div {
        line-height: 100%;
      }
      .apple-link a {
        color: inherit !important;
        font-family: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
        text-decoration: none !important;
      }
      #MessageViewBody a {
        color: inherit;
        text-decoration: none;
        font-size: inherit;
        font-family: inherit;
        font-weight: inherit;
        line-height: inherit;
      }
    }
    </style>
  </head>
  <body>
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
      <tr>
        <td>&nbsp;</td>
        <td class="container">
          <div class="content">

            <!-- START CENTERED WHITE CONTAINER -->
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="main">

              <!-- START MAIN CONTENT AREA -->
              <tr>
                <td class="wrapper">
                  <p class="align-center text-xl font-bold">Daily Redact 🚀</p>

                  <!-- For each article... -->
                  <div class="mt-3">
                    <a class="font-bold" href="[link1]">
                      <h3>[title1] (with link)</h3>
                    </a>
                    <div>[summary1]</div>
                  </div>

                </td>
              </tr>

              <!-- END MAIN CONTENT AREA -->
              </table>

            <!-- START FOOTER -->
            <div class="footer">
              <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td class="content-block">
                    <span class="apple-link">
                      Have some feedback or want to make adjustments? Reply to this email!
                    </span>
                    <br> Redact's Team 📪.
                  </td>
                </tr>
              </table>
            </div>

            <!-- END FOOTER -->
            
<!-- END CENTERED WHITE CONTAINER --></div>
        </td>
        <td>&nbsp;</td>
      </tr>
    </table>
  </body>
</html>













<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Redact 🚀</title>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #f9f9f9;
      font-family: Arial, sans-serif;
      box-sizing: border-box;
    }
    .container {
      max-width: 36rem;
      width: 100%;
      padding: 1rem 4rem;
      margin-top: 1.25rem;
    }
    .content-center {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .text-center {
      text-align: center;
    }
    .text-xl {
      font-size: 1.25rem;
      font-weight: bold;
    }
    .font-bold {
      font-weight: bold;
    }
    .mt-3 {
      margin-top: 0.75rem;
    }
    .mt-5 {
      margin-top: 1.25rem;
    }
    .mb-2 {
      margin-bottom: 0.5rem;
    }
    .underline {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="container content-center">
    <h1 class="text-center text-xl font-bold">Daily Redact 🚀</h1>

    <!-- For each article... -->
    <div class="mt-3">
      <a class="font-bold" href="[link1]">
        <h3>[title1] (with link)</h3>
      </a>
      <div>[summary1]</div>
    </div>

    <!-- Conclude with this: -->
    <div class="mt-5">
      <div class="mb-2 text-center">
        Have some feedback or want to make adjustments? Reply to this email!
      </div>
      <div class="mt-3 text-center">
        Want to share Redact with a friend? Send them our website: 
        <a href="https://redact.lofipapers.com" class="underline">https://redact.lofipapers.com</a>
      </div>
      <div class="mt-4 text-center">📪 Redact's Team</div>
    </div>
  </div>
</body>
</html>
"""



