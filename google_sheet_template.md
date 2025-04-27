# Google Sheet Template for TikTok Content Performance Analyst

## Required Structure

Your Google Sheet should have the following columns:

| Column Name               | Description                                   | Required        |
| ------------------------- | --------------------------------------------- | --------------- |
| Title                     | Title of the TikTok video                     | Yes             |
| Hook                      | The hook/opening of your video                | Yes             |
| Caption                   | The caption text used for the video           | Yes             |
| Views                     | Number of views                               | Yes             |
| Likes                     | Number of likes                               | Yes             |
| Comments                  | Number of comments                            | Yes             |
| Saves                     | Number of saves                               | Yes             |
| Hashtags                  | Hashtags used (optional)                      | No              |
| Like-to-View Ratio (%)    | Percentage of viewers who liked               | Auto-calculated |
| Comment-to-View Ratio (%) | Percentage of viewers who commented           | Auto-calculated |
| Comment-to-Like Ratio (%) | Percentage of likers who commented            | Auto-calculated |
| Save-to-View Ratio (%)    | Percentage of viewers who saved               | Auto-calculated |
| Save-to-Like Ratio (%)    | Percentage of likers who saved                | Auto-calculated |
| Analysis Report           | Generated report (will be filled by the tool) | Auto-filled     |

## Spreadsheet Formulas for Ratios

You can use these formulas in your Google Sheet to automatically calculate the ratios:

### Like-to-View Ratio (%)

```
=IF(D2>0, ROUND((E2/D2)*100, 2), 0)
```

### Comment-to-View Ratio (%)

```
=IF(D2>0, ROUND((F2/D2)*100, 2), 0)
```

### Comment-to-Like Ratio (%)

```
=IF(E2>0, ROUND((F2/E2)*100, 2), 0)
```

### Save-to-View Ratio (%)

```
=IF(D2>0, ROUND((G2/D2)*100, 2), 0)
```

### Save-to-Like Ratio (%)

```
=IF(E2>0, ROUND((G2/E2)*100, 2), 0)
```

## Instructions

1. Set up a Google Sheet with these columns
2. Enter your TikTok video data
3. Share the sheet with the service account email from your `credentials.json` file
4. Use the TikTok Content Performance Analyst to analyze your videos

Note: If you don't include the ratio columns, the tool will calculate them for you automatically.
