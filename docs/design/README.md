# Admin visual reference and QA

`admin-concept.png` was generated with the built-in Image Gen tool as a concept,
not embedded as the UI. Prompt: Vietnamese Lost & Found moderation admin;
white canvas, navy sidebar, green active accents, four summary metrics,
seven-day chart, report table, matching login and mobile states. Required
labels: Tổng quan, Báo cáo, Bài đăng, Người dùng, Nhật ký, Đăng xuất.

The implementation uses code-native text, controls, tables and chart bars.
`admin-desktop.png` and `admin-mobile.png` are browser captures with live demo
login and real API data. Browser plugin was not available; Playwright was used.

| Comparison | Implementation and intentional differences |
|---|---|
| Palette | White background, navy sidebar and green primary/chart tokens. |
| Layout | 232px desktop sidebar, open metric row, thin table borders. |
| Typography | Local Geist font includes Vietnamese; replaces concept's generic sans-serif. |
| Copy | Actual report codes and server metrics replace concept sample values. Chart correctly describes posts, not reports. |
| Icons | Consistent Lucide outline icons on navigation. |
| Mobile | Five-column navigation at the top replaces concept's bottom navigation; all destinations stay visible. |

The scaffold intentionally contains read screens and authentication. No
moderation controls or unsupported action buttons are shown.
