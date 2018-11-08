# BART Arrest data

We are interested in knowing more about BART police's arrest data following a smug comment
made by a BART board member on Twitter. Do we decided to do a public records request for it.

```
Last night on Twitter a board member, Nick Josefowitz stated: 

"Using data, better analysis, and new strategies, @SFBART police were able to increase arrests by 40% year over year. We need this approach at SFPD, and as Supervisor I intend to make accountability and modern police tactics paramount. #NoMoreExcuses"

https://twitter.com/josefow/status/979069932896997376?s=21
```

# California Public Records Act Request

Below is the exact CPRA request we sent to BART:

```
Greeting FOIA officers:

Last night on Twitter a board member, Nick Josefowitz stated:

“Using data, better analysis, and new strategies, @SFBART police were able to increase arrests by 40% year over year. We need this approach at SFPD, and as Supervisor I intend to make accountability and modern police tactics paramount. #NoMoreExcuses”

https://twitter.com/josefow/status/979069932896997376?s=21

Therefore, under  to the California Record Act, I am requesting:

For the years between 2012-2017 (the full calendar year beginning Jan 1 to Dec 31st) I request the record for each year:

* Records sufficient to show the number of arrests on BART
* Records sufficient to show the race of an individual or individuals arrested.
* Records sufficient to show the charges against an individual or individuals arrested.
* For a given arrest, the unique case number referred for prosecution.
* (If known) the outcome of each case

Please acknowledge this request is being made by a member of the press and I request you waive all fees in the public interest. Please do not hesitate to reach out to me if you have any question about the size or scope of this request.
```

### Scripts

* `detect_pdf.py` - simplified version of [Google's PDF OCR sample script](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/vision/cloud-client/detect/detect_pdf.py)

* `ocr_results_to_csv.py` - custom code that pulls the results of Google's PDF OCR script, parses out the results, and outputs a csv file.


### Fields

* Case_number - One thing to note is that this is not a unique id for a row. There are a few case numbers that span 2 rows, I imagine meaning two individuals were arrested at the same time.
* date_of_arrest - Date of arrest
* sex - M / F
* race - Race code, includes A, B, C, F, H, I, O, P, S, V, W, Z
* dob - date of birth
* location - Location, which is a bit annoyingly structured. It seems there is a different location if it wasn't actually inside the station.
* crimes - '|' separated list of penal codes, health and safety codes, etc. This data was all over the place in the PDFs.
