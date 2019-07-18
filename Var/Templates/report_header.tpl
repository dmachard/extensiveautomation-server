<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
<!-- REPLACE_ME -->
</script>
<style>

body, table {
    background-color: white;
    font-family: Verdana;
    font-size: 13px;
}

#general {
    border-spacing: 0;
    border-collapse: collapse;
    width: 100%%;
    font-style: italic;
}

#general td {
    padding: 6px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

#description {
    border: 1px solid #ddd;
    border-collapse: collapse;
    font-style: italic;
}

#description td {
    text-indent: 0em;
    padding: 5px;
    text-align: left;
    /*border-bottom: 1px solid #ddd;*/
}

#steps  {
    border-spacing: 0;
    border-collapse: collapse;
    width: 100%%;
}


#steps td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}


#steps tr:hover, #general tr:hover{
    background-color:#f5f5f5
}

#statistics {
    border-spacing: 0;
    font-style: italic;
}

#statistics  td {
    text-align: left; 
    margin: 0px;
    padding: 0px;
    border: none;
    padding-right: 8px;
}

h1 {
    font-size: 17px;
}

h2 {
    font-size: 13px;
}

.header {
    width: 25%%;
}

.report_header {
    border-bottom: 1px solid #000;
    padding-bottom: 5px;
    margin-bottom: 30px;
    text-align: center;
    font-size: 10px;
}

ul {
    list-style: none;
}

li {
    text-indent:1.6em;
    background-repeat:no-repeat;
    background-position: 0px 3px, center;
}


.step-section {
    text-indent: 0;
    background-repeat:no-repeat;
    background-position: 0px 3px, center;
}


.test_disabled {
    color: grey;
    font-weight: normal;
    font-size: 13px;
}

li[data-type="testnotexecuted"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuOWwzfk4AAAG1SURBVChTVVA9S0JhGH2Haipy0MCptiYnZ71zINcPFAe/FZzU/ECUq6CiqPgtOlwHBxEcRIWQxugX2C+I2hxqDqFb9+28N4s68PBy73Oe85znkL/odruqdrutQ3GdTseA78vhcHi8b/9Hs9k0ormezWbb1WolL5dLaTKZPPX7/UWr1dLvad+o1WpGNLYgy6VSibrdbur3+ymIdD6ff/Z6vQ0EzxVyoVBQNRqNNdTkdDr9aLfbQw6H4yiVSl3B2ut0OqXj8ViCqDAajQ5JPp/XDQaDbblcpj6fL8Rx3AG886IoPtfrder1eh/Yi9pkMplTkkgkOAzIeClTZmQc/MKUse3G5XJpBUGgEPyIRqMaEolEDPAn5XI5pnLFlBnZYrHcm83mC1g+KxaLFP1dMplUk2AweIlVT2wtUnplL1Pek1UIQaxWqzQWi92Be0Jg4xiJLHDLJ5KisPYQj8e12HqGEhHIWzabfcct1+w+JSkM6fFjg5QkpsbiBJlWKhWKtBj5lt2ikH9gs9nOnU6nwAYDgcAHaufxeO5g79pqtf4n/yAcDh9i2ylIGpPJpOZ5/uTXhgJCvgCUEPATIkLmtAAAAABJRU5ErkJggg==');
}

li[data-type="testdisabled"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuOWwzfk4AAAG1SURBVChTVVA9S0JhGH2Haipy0MCptiYnZ71zINcPFAe/FZzU/ECUq6CiqPgtOlwHBxEcRIWQxugX2C+I2hxqDqFb9+28N4s68PBy73Oe85znkL/odruqdrutQ3GdTseA78vhcHi8b/9Hs9k0ormezWbb1WolL5dLaTKZPPX7/UWr1dLvad+o1WpGNLYgy6VSibrdbur3+ymIdD6ff/Z6vQ0EzxVyoVBQNRqNNdTkdDr9aLfbQw6H4yiVSl3B2ut0OqXj8ViCqDAajQ5JPp/XDQaDbblcpj6fL8Rx3AG886IoPtfrder1eh/Yi9pkMplTkkgkOAzIeClTZmQc/MKUse3G5XJpBUGgEPyIRqMaEolEDPAn5XI5pnLFlBnZYrHcm83mC1g+KxaLFP1dMplUk2AweIlVT2wtUnplL1Pek1UIQaxWqzQWi92Be0Jg4xiJLHDLJ5KisPYQj8e12HqGEhHIWzabfcct1+w+JSkM6fFjg5QkpsbiBJlWKhWKtBj5lt2ikH9gs9nOnU6nwAYDgcAHaufxeO5g79pqtf4n/yAcDh9i2ylIGpPJpOZ5/uTXhgJCvgCUEPATIkLmtAAAAABJRU5ErkJggg==');
}

li[data-type="testdescription"]{
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAf5JREFUeNqkUz2LFEEQff01O3vril4iiIZ6mYEiiIj+AeECMRI2E82OC/0LwiGmouJP0NBEkYMzE0QwEUyMRMU7bw/cnelqX3XvLIdMIDgzPV3VPe9Vvaoeg55r++q559LG9STFNxZwzn66sv3h7N/f+j4CiXH94mQCnPhSFr6exvtnT870fdtLkCRBpMXew5fZX705QWhm+GcCk3QkuHqw8BOsNKju76SjsylcirDGwFu700vgkiFAYKtCgBj5CG5fu4STwx9w3Dv4VePxm7eXewl8a2FYQOerZQaJQ3hvvd6HZQZ3zoe85q9v4WcTcYwBEFnt3zURTxMJWtjgFwQRSWe+j9eWBKmrFryCH9zYBAafISSYyik0j16RgLq7DGQBoO4jwVKimiaTeo08lV28+/gCYoC1tVvwCj5EYKVEM7xHmoEUgmUXGjOFqcqBmdP2OV3WoJOQ4fRpjDwzkGJnAp0be7AkaGkrxPIYLiWweCrbWmZQaQ1IQFvXvFLP7T4SO8buZbvEJIkPXa1KNIJWKpdr4DsJOrduF2aQa0R7T6EZFMKhLqvP5XHlmQFlOMeAPEyJQdrRt6yJAZCG3zHEqv4RQBWW6AH3arZ4PB5neWElYO5qmI2791Ib9eyXlMTz1AUOE1V56QK3vILaGVxsFmuGGbks9gL+4/ojwABQE8JXt4MgNgAAAABJRU5ErkJggg=='); 
}

li[data-type="testglobal"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwAAADsABataJCQAAABp0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTFH80I3AAAA3UlEQVQ4T52SOQ6DMBBFOSbXQjQUSFCxmh263CBllC6l6XKGOONJHOzBLMqTPjYe+3mQcCRCiL+DRFH0YIzNTdNwlbquOazxsiwxWZbxPM/nMAyfQRBcDEHf9zA/TxzHdxgWAZix4LruYSS+799gWATQIhbO4nmeKSiKAgu2G2kkK0Hbtlg4y+oTlIDeJK6w5yCGYIXlAA0Kuq7D/Zsd2NAFm/+BLlBzEhQMw4B7djtQo0IXjOP4XSVQgeUdBdM0fRYp+gGKLqgq9pJdJEnyS5qmi2An8NyJ5YAZR7wBVhT1+/N4SMoAAAAASUVORK5CYII=');
}

li[data-type="testplan"]{
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwgAADsIBFShKgAAAABp0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTFH80I3AAAA3ElEQVQ4T52Suw2DMBRFM1OmYZysgGgoLEHF1/yhyxZRuiiV6Zghjn0Vgm2MQFzpyIC5xw+Jiwzn/DRIEAQvSulYVRWbKcuSiWcsz3OQJAlL03QkhEy+7981Qdu24vp4wjB8imURCDM2HMfZRcbzvIdYFoEYERtH47quLsiyDBu2E01kVoK6rrFxNKtPmAXmSVeyjyYwYyuYQNA0DQpbE7z5TWMl2PoPVIFaUu8h6LoOhdMT9H2PghlVoJZUIBiG4VfRM7+0KygK+pFTRFH0J45ja8EEP8MWtoIO519p/+lLSCAcmQAAAABJRU5ErkJggg==');
}

li[data-type="testsuite"]{
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwgAADsIBFShKgAAAABp0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTFH80I3AAAA30lEQVQ4T52Suw2DMBCGs0g2YCDGyQqIIhRIUPE0b+iyRZQuSmW6zBDHPsWAzzggfumTLc73+ZB8EmGMHQYSBMGTEDJWVUUlZVlS/o3meQ4kSULTNB193397nndTBG3b8v3+hGH44Mss4GYo2La9iYjrune+zAI+IhT2xnEcVZBlGRTWbsSIaIK6rqGwN9ovSAG+6Xy1NlEEOGsNGBA0TQMNpgle7KKhCEzvYCmQewwIuq6DhsMT9H0PDTjyEEYTDMPwa1GzbMAogqIgHzFFFEUTcRxPh/4Bj8HEWoOKxb4HtLDbsvzXwAAAAABJRU5ErkJggg==');
}

li[data-type="testabstract"]{
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwgAADsIBFShKgAAAABp0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTFH80I3AAAA4klEQVQ4T52SOw6DMBBE0+ZqOQHHyRUQDQUSVHyM+RnocosoXZTKdDlDHHsVB7zYAjHSyLus5nmRfFISQhw2KI7jJ6V0apqGa9d1zeU3XpYlOM9zXhTFFEXROwzDmwFgjMl6v5IkechjBkgyDDzP27RSEAR3ecwAuSIM9sr3fRNACIGB7UZspRWgbVsY7NXqFzQA33S+sE0bACxbABsAXddBwLXBS1xXNgCud7AE6Br3AOj7HgKHNxiGAQJYS4CucQ+AcRx/EVO2AO4BUFX0o7ZI0/TvLMuMkMvwGFy2BUwz8QWKq7jDzTSe9wAAAABJRU5ErkJggg==') ;
}

li[data-type="testunit"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAadEVYdFNvZnR3YXJlAFBhaW50Lk5FVCB2My41LjExR/NCNwAAANtJREFUOE+dkjsOgzAQRH1MjpMrIBoKJKj4mr/pcosoXZTKdJwhznoVB7DjYDHSkw07O7tIECkhxGlQcRw/KKVz27Zc0TQNh3e8qiokz3NeFMUcRdEShuF1FzAMA9zdlSTJHY41AJKx4HneIVJBENzgWANgRSy4yvf9fUBZllj4NVFHygjoug4LrjI+QQXok6Dkgn2DjekfhPR9jw22DZ7ism3Qn+3/gTIdBozjiA2nN2CMYYMuZToMmKbp07KXMskGHVUDCKlr+pJbpGn6JcuyrcmOHGTDMBsQ8QYWfW9ntX89wgAAAABJRU5ErkJggg==') ;
}

input {
  display: none;
}

input ~ ul {
 display: none;
}

input:checked ~ ul {
 display: block;
}

label { cursor: pointer; }

label:hover {
   text-decoration: underline;
}

</style>
</head>