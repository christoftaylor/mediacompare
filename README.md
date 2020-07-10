# mediacompare
python script wrapper around [mediainfo](https://mediaarea.net/en/MediaInfo) to allow for side-by-side comparison of two media files



Known issues:
   - It only compares the first video and audio stream it finds, 2nd+ are ignored 
   - It outputs to three columns to provide a side-by-side view, but column widths aren't pretty
   - Column width is set up the 'General:Complete_name' field, and field longer will get truncated. This affects the 'Video:Encoding_settings' and a few other fields. Is by design. 
   - It tries to keep the order, but fields in the 2nd file not present in the 1st get shuffled to the bottom rather than injected into the middle. I'm not sure how to clean that up.
     
     
Future ideas:
   - only print out interesting fields, drop things like 'Encoding_settings'
   - add a -t option that creates a tab-separated output instead of columns, won't need to truncate

