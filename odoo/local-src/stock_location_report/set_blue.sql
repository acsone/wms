update stock_location
set color='blue'
where zone='A' and (
       (box='4' and corridor in ('A','C','E'))
    or (box='A' and corridor in ('B','D'))
    or (corridor='A' and shelf in ('9', '10'))
    or (corridor in ('B','C','D') and shelf in ('13','14'))
);

