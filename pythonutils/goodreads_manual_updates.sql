-- Manual updates for data that goodreads doesn't classify right 

-- Mrs. Dalloway ISBN10
update goodreads set isbn = '0241371945', isbn13 = '9781912714926' where book_id = 46749;