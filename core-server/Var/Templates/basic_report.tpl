<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script></script>
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
    border-spacing: 0;
    border-collapse: collapse;
    width: 100%%;
    font-style: italic;
}

#description td {
    padding: 6px;
    text-align: left;
    border-bottom: 1px solid #ddd;
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

#testcase {
    list-style: none;
    margin-bottom: 5px;
}

#testcase li {
    text-indent:2.8em;
    padding: 4px 8px;
    background-repeat:no-repeat;
    background-position: 20px 5px, center;
}

ul {
    list-style: none;
}

li {
    text-indent: 4.8em;
    background-repeat:no-repeat;
    background-position: 0px 0px, center;
    padding-bottom:5px;
}

span {
    padding-bottom: 5px;
    border-bottom: 1px solid #ddd;
    font-size: 11px;
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

.test_section {
    margin-top: 10px;
}

.test_main {
    border: 0px;
    font-weight: bold;
    font-size: 15px;
}

.test_title {
    border: 0px;
    font-weight: bold;
    font-size: 13px;
    color: black;
}

.test_time {
    border: 0px;
    font-weight: normal;
    color: grey;
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

li[data-type="pass"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAABp1BMVEUAAAAsTQBGagwsTgD///9CZwgtTwAvUAAqSgBCZgYxUgD///HL/2yi1FFWfBVUeRNSdxFPdA5GagdNcgxFaQVLcApFaQVJbglFaAVHbAdDZwNGagYxUgJLbw5EaAxfhiGBrENvmDErTQBbghyCrEaMt1FpkSo2WQBZgBp9p0B/qURXfBhXfhdehR08XwJXfRd4oTqCq0lrkjBOcw9SeBJwmjF4ozpfhh80VgBUexVxmzN7pEFmjSpIbQtRdhFpkipxmzNbgxtQdhBrlCxzmzhhiCVIbApWexdpkCxrkytnjyZrki9dgx9HbAlDZgNWfBhiiCRjiiZYfhpHawhBZAJSdxNagRxcgh1UeRVGagdBZQJOcw5UehVVexZPdRBGagZCZgJLbwtPdA9McQxFagZDZwNIbQhJbQlFagVDZwNDZwOWwl6PuVaOuFaQuliIsk6HsE6HsE6AqkV/qEV/qEV3oTt4oTx3oTx2nzx2nzxulTJulTJvljJvlzJulTJulTJljChljChmjShmjSlljChljChdhB9dhB9dhB9dhB9WfBdWfBdPdQ+yX+jcAAAAa3RSTlMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhkISdB+CEfe9noJR93wUjhWCUbd/7QiQNn2eghF3P+0H0fY9XpK2/+0H3L39On/tB8Lg/f/tB8Kg/f/sx8Kg/f/sx8JgfezHwl9pSAFCsgArQkAAAABYktHRASPaNlRAAAAB3RJTUUH4AcICgkUa4uvPwAAALVJREFUGNNjYMANGGVk5ZiQ+Mws8gqKSqxwPhuLskq2qpo6jM/OoqGZk5unpc3AwaKjq8fJxa1vkF9QaGhkzMBjYmpmbsFraVVUXGJtY8vHYGdfWubg6ORcXlHp4urGz8Dg7lFVXePpVVtX7+3jKwA0zc8/oKGxqbmlNTAoWBBkvFBIaFhbe0dneESkMMRCkajomK7u2Lh4UZgTxBISk3qSU8QRjpZITUvPkET2llRmljROPwMAtsMmm//sxoMAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTYtMDctMDhUMTA6MDk6MjAtMDQ6MDBLoajAAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE2LTA3LTA4VDEwOjA5OjIwLTA0OjAwOvwQfAAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAAASUVORK5CYII=') ;
}

li[data-type="fail"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAACGVBMVEUAAAC4NxjUYSXUYSW7Ohm4OBjRWCK7OxnAQRvCQxvMTx7NUh7GSh3GShzHSxzHSxzFSBvFSBvPRhnPRhnNQxfNQxjDPhfCPhfCPRXCPRa9Phm9Phq9Pxu/ORS/ORS9Pxu+Pxy+NxO+Pxy3NRjMVyHHTx/HTx/OWCK6OhmlHRHVXyPqgC3hcSnDRRzDRRzhcSnrgS7XYSSrJROyLRXVXCLreyrhbCbDRRzsfCvXXiO2MxfISx3jbibseynfZiTkbybJTR3DRRzUXCDgbSTgbSTTXCDDRRvAQBrQVh7cZR/cZR/QVh7AQBq+PxrOURvOUBu+PxrGQRrXTRnWTRnFQRrFQRrVSBbVRxbFQBrBPhjRQRPQQRPAPRjBPRfHOg/FNwvDOxLFNwvHOg/BPRe8QR6/ORPBMgvCMAjBNg++PRm+PRnBNhDCMAjBMgq/ORO8QR+8RCK/NxK/Lwq/Mg6+PRm+PRm/Mg6/Lgm/NxK8RCK+QBy+ORW+Oxe+Oxe+ORW+QBzuhC3vgizvgizuhC3qfCnneijoeijoeijneijqfCnjcSTjcSTkcSTnciXjcSTeaCDeZyDeZyDeaCDYXBvZXRvZXRvZXRvYXBvXUxfUUxfUUxfUUxfXUxfWSxPPSRLPSRLPSRLPSRLPSRLWSxPRQQ/KPw7KPw7KPw7JPw7KPw7RQQ/GNgrGNgrGNgrGNgrGNgrCLgbCLgb///82ZZKCAAAAgHRSTlMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhGHh5JCQZ19LUgILX1ewcGdfS1HvV7CEXx/7vySB21//+0HR+0//+zHx67ux4gvbwfIba2IB63th5G8f67/vFGBnTz/7QeHrT/9HUGBnTztR8ftfR2BghFHh5HCCe/cMoAAAABYktHRLKtas/oAAAAB3RJTUUH4AcICgoFKhbcDgAAAMpJREFUGBllwb1KA1EUhdH9nXvOzCRMKVaC4A8IdgEfQCwCGhBB8A0DKRVjkaBWKlZWFoJCUikIQqZTxPHWupb+QmINXn6U1uH5Wyg2yJ60Rfb4SbUNB4xRO2AMD2ZVdRhRZhFHRWHUO9AH1LbpAu7S18dqmm2mZBYT99vG1NxHeFZExM1CLpkTIHBMQku79AEB51y+s7zHPpnaNnHK1M0p4QwxgBIzK8upTzqdbvc6XdW1oZVjshEnZMN5UvPWixjNF6899+FM//wC9mUvJZVNXRAAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTYtMDctMDhUMTA6MTA6MDUtMDQ6MDBmJ3QQAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE2LTA3LTA4VDEwOjEwOjA1LTA0OjAwF3rMrAAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAAASUVORK5CYII=') ;
}

li[data-type="undef"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAACGVBMVEUAAADqvSrntCTTgQfTfwa+XAD/3EP7yTi3UADXhQnWhAnGbQD//////5/GbADaiAnaiAnMdQDLdQDfiwrfiwrPeQDPeQDkigfkigfcfgDcfgDbmBbntSrntCnalhXOdQDstS3ssyvMcQDinBr2wjn0vzjhmxnTfwTwsSnxsSjSfQPkmhf4uTD6ujDkmhjWgwbwqSLwqCLWgwaDFQDnmBTmlxN2BQDahQfyoBnyoBnahQe3YgDokg3okg24YwDdhQXylw/zlxDdhQW5agDqiwfqiwe/bgDOeQDriAXriAbOeQDGdwDkggLjggLGdgDVewDgfwHkgAHkgAHkgAHkgAHkgAHkgADkgAHkgAHkgAHkgAHgfwHVewD60ET60EPuvUDnuD/yvTp+aTZZTjXZqznrsTRbTjM4NzPGmDT5tS7trC5iUjI9OTPLli/7ti73rSX3rCfwqCdpVDBCPDLXmCn5rSf3rSX3piH2pSD0pCByWC1JQDHhmCL3piD3piH3oBn2nhn2nhn3nxmNZCdoUCzrmBv3nxn3oBn2mRP1mBP1mBP2mBPWiBjIgBr0lxP1mBP2mRP3kw31kQ31kQ32kQ3tjg96ViZZRizVghT3kg31kQ33kw32jAj1jAj1jAj1jAjviQmLWx9tTSXZfw72jQf1jAj2jAjxhgPzhwPzhwPzhwP0hwPvhQTshAXzhwPzhwPzhwPzhwPxhgPE+FHNAAAAXXRSTlMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAkh4YiErSxEWT6+WAby8gZeP38cibb2SUCiIcCMuPiMgWengZB7e5CB6OnCRvV2B0JoqIJHXqjpKSkpKSkpKSjfR6FOsSmAAAAAWJLR0QMgbNRYwAAAAd0SU1FB+AHCAoNE5GD/5gAAACVSURBVBgZXcExCwFxAMbh9/e/V+c6kcFAkgw+gpJMZl/UBzAyXL6DQZLMkkGS5K67QZ5H/1CBHnD5KIdyUZ85Gee3JEuqYQIm8lNCUjJgCuw4PSRLKcaAiZp3IbWGTClkHG9C7REzSlsOVyuYOiUTRGfMgtIrXrN3MAmlKDaBBUsqr5gVNimVWoyxSak0wNCd8Gujf1853Bdje+3x2gAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxNi0wNy0wOFQxMDoxMzoxOS0wNDowMIYapfkAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMTYtMDctMDhUMTA6MTM6MTktMDQ6MDD3Rx1FAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAABJRU5ErkJggg==') ;
}

li[data-type="passed"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAARCAYAAABn5wTeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuOWwzfk4AAAIvSURBVFhH3ZdNT1NBFIbnPxCjRqNGRWIMG0D84iu4gYYGNsqKBEkTXZkYUIzRaEjpj8Cw5WOhKIVqDLRQoYkssN3TNhYI7b6wfT0z91rOlLkDLrknedrpec/MOW8nN00FALF7UELo12vURjtR86nh1FMf68KzjbeQvqQ/ZbBu4SHOfG70HdejHSjs70I83XiDs3NNvkX6E21Lj3Fu7rZvaV/qhzj/pRl+R1ygFysrU8jJx5dHeQrdmr6OYb6H6N4quMVOLG+eQDP1olC6QeNn2hAXv96BlVU6nEwFWC5AQ+a2BtV6uEjNiuuVz+Y9g5goFzCx+r8aQ2rFMMuFsQx3H68zIC7N34WV5DQ1nkYPy/VkyWT2Ca3DiCuN3uk2R/geGuBj8nBPheO0ql6aVgprucM5WJ0BcXn+HqyooaqCBgmSFqQm8bRTx9cO42ScRWn8eM3UCym8/KdpZxDplDKp5QyIK9H7sJKcQb48g+ARLaIPKsNY5/CKfpfz2SG75tmLkFopouWcL5bVeCCuLjyAlZ9O497qfCZFNxDRcqM0bCLjalV7TqR59ZJITesXQYJueZTXeCCuLbbAytosNZ5Fn5YPYbK8jck1niOUAae2L7ftXq8T+VyoUuepyV5ujofSDVoiw3pbELWLrfA7IpAcwI1Yq2+R/sTzzXeoi7X5lhe/P0DsHOyh8UcXbn5r9x3S15/9Hbj/J/fI8Xu0xHtx63vHqadz5RFG0mPKIADxF9FwqJMJeBK/AAAAAElFTkSuQmCC') ;
}

li[data-type="failed"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAARCAYAAABn5wTeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuOWwzfk4AAAIsSURBVFhH3ZfbahNRFIa3iKAIVkQEUZHiA4heqvUQ2lCRekBBQaF3QswkRm/F4n1SqfT8DCX1tgcfwOYVbOhFpxbBCzvJnkySmfndazoT9owTsr3dCz4y+f91mJU5QBgA5v3eB//8Fn+eXtEC6/VN8C/vQXvRfsGC1uR1HDwZ1g7r1VV4v3bB7LKBg0eXtYX2Y838PVgPL2pL08iAWRMXoDvMenAeypSW4dGjLIX3dVzyvqEVq3mHbqSRv7cMHvNDPewlR3cm3Qv0ZI8BsMb9c1CmuASvVkr1nBrg1jbhrWYlvQQXm3DomGr3lsB7Xkg/PfJi86hfHZ2ilKMAa4yfhTKFRTG0mOIV4ZqL4PRJS8l69J1qg5zIC+mnR15iHl+tix9yNKYNgjWyZ6CMsZC4fTbgCJ1X63CnD3Pk40a2IJY8zAlqzQXwQJf4pyeFVLNViOdPb8CrZuLaAFhz7DSUyc+LoUZCN8QiiTDnYfc8ccJRbU+X6KdHXmKeXd2GW5FyFGDN0VNQ5s2cGJqPa5V1IKE5W+L5rNBxXiy5Dod0qjXnYEt5Af30yIv1lvr9B4xnTkKZ3Cz87zlJG0HX3EY3J+UQ5TVxNWfRyuTESa2hTRrVhhe6F9QrTRfhr4ykem45MUsBxu+egO6w1uQ18DvHtYX2Y+2Pz2HfPqYt7U8vwfz9HfFmG4J966h+iL188c4I/k/6P3fQ+fAMrRtHtMB5fAmdqRfwd3+I9cD+Am/2WWbdwFFuAAAAAElFTkSuQmCC') ;
}

li[data-type="undefined"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAARCAYAAABn5wTeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuOWwzfk4AAAH6SURBVFhH3ZfPShtRFIfvW5QiVApFWxWsgoi7gl10VUHc+ASiD1BTNfgkJg1uiohBpUqxrSbVhBRKNTEaMGTShoYkU0OC+T/Cr3fmjpO55grj7JwDX8ic7/xm7gnZDAGgkQrN4MT/Aj8/PnrwRLdeQgrP0bXYbtrH6WY/jtceO46Yv1dblPyJzCK23uVY1P1Icm8c8Y0njiX55TVIwt8Np0MuNp/CMoEVtHLvuF4+B1R/6Q77yN/p+NL66pzAqXVXrpV8a9zfKiS1/QyWCXrQyru4npynBzrWXUXiPOe4nAtVSCgFb3Ie/DWcCcHz7EDSn3pgmUMvlMJ7rvevANRO2i6bSrNrgTPn1DklNclcxYusyRkIcnYgmZ3nsMzRB/rQRa5XpIvUo2a3iDoCKApdO5eJBqBIU8zpf8V2sXyn0/v3hGR3+2CZkI8edonrlQppVEK3XCwA0O8lumQjJs7JUrrtqj7IJmcgyNmB5D4PwDpuNBBEWXQd9uFadhuzZZn99o3TTteRo0teGs5ER84eRN4bxL2If2en16sZ1/uRVXqgZdPsMpo3XnVs3Cgup/fMdf17WnBPe5Di1yE4HXIVmUL527BjUfcj9fg8rg5GHEv9bIG9itSOXqEWHHUedC91P+N9UjlfQDPyBs3DsQdP68cElIRbWxAA+Q8wzN5a0GsvzQAAAABJRU5ErkJggg==') ;
}

li[data-type="norun"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAARCAYAAABn5wTeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuOWwzfk4AAAItSURBVFhH3ZfdTttAEIX3QasKpbQhkKZpgFIUohRoq8iAXAoipb2BJsTBiaLe85eA+gKN88Mj2Ia0b3C6u/aaJU6813ilT56ZnT3HI9sXJgDI/WiE/fI3pNIZPJtJPHkybxdRPvwONhebjw+4kMnieWI2dszRh+a6dyDlwx+YmU3GFjYfWStuIPEqFVvWPmyAvJhbQNwhL+dfQ0npEjZ6OJJqRxbwpyLyLZzZ7BsX63FvANcZW9bJw56IfQIPpX80JJnOQonWhu049CaMoHZMTbpVFhvo0nv1Yp9qj1Z6OBa5gOlIGsn0Ds6p7rk2aU/yiPRXQ1JvclCy3YHdq6N05aJb82oVOgePa33YV3roDOsN1X2dh5qOC8fFxfakPckjyl/qnwaZzy5ByQ4zOaXxKSwMUKE1ZmIZSyi1XX4NnTEGsNtfHteYDn9HpcV1/T0R+wiPKH+5fxoknXsHJfo1nH7Di+sDgMbVPjWpe7nT+Ro6o3XccF3WyTVgudfQJu55VPsuLvWxvXF/qX8aJLP8Hkp2b+AMmkFeoz78IZgsb9KvT8Q+5pBWhqiJXDCmw/uCnOnIZ6Q80l8Nya7koWTvN5xhS6q1vMEaIj8AfWuldQsj6JUI6eRh0DmdmwMvb9z6570V6Cv9oyG51QLiDtF297GYL8YWNh/5WTexXFiPLVWzCTL6+w+FTxpWih9jB5vr7n4E/j/JBj0xW9jc0rG6/vnJU9L3YDR/8QEBkP+ydWsRfu3zEAAAAABJRU5ErkJggg==') ;
}

li[data-type="ignored"]{
    background-image:  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAARCAYAAABn5wTeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuOWwzfk4AAAJ9SURBVFhH3ZftThpREIbPhTaNobaKH5RiLTVKqLY1BDFoJVLbP1qQpUhM/1crH+kNCAv0EnZXae/g7czZD85y8ALcSZ7knHnnnTMT1h8KAOJ+PEap/BnxlQSezMUePYlXayiffAHvxfvJBZcTSTyNzUeORfrRHOcOonzyFXPzC5GF9xNb2R3EXsQjy9a7HYhni8uIOuL50ip0ziW3MHEa5Pbw0+K/40ncVjwt9wtWqHYVp31F17xKrfRORZ/ff0CjkH1naJP3woiFlSR0DEmPhjmT931c2UCvGq7pwcZVns75FizbhtVnn6uf0ZJuPddNeasmZbze7FV87ltq3xZ2A01B8ynzqHWEiL9MQacu6WGACt9rA5qJc9N1HoU2LNJzNw56NTdXoT3kmbzWTVHzcK3Me96JVsS17eC6QGfW7DZyii9A8yk9lRwjlpKvofNd0scQFb4bQ1itA087oCHk1yGjb1Bunx8Me3hJ1nItx60Jenv4Pdnr9QpC9qKaWZo/U/DmjJ5qjhArqTfQuZDwwFW+14fAgHPhunybFqjTudiB7etebZV+fKnR3W5/mumVedXLbzod5P061tS7SsjnEsyj5BiRWH8LnabExAg1eS+BvgTYnZJS4+bMBp0Pu7CH7HG1Gu3JITXZxz97NEaU8XpPeaXm31lzuij4msq0LzRvGJFMb0LnUmLiDwwlb/BsSpgXnnb0G/aIPX4texU9fQz6apVQ+mpe9x27e+xqnkONh7TJe2FEaiODqCPyhyWsbWYjC+8nvtUbWM9sR5Zqowkx/vsPmY95pLMfIgfvdXc/hvx/khc9b1zi/V4RG9u7j55c8QhG84dcEID4DxG9o/RoGU7PAAAAAElFTkSuQmCC') ;
}


.isexpanded {
  display: none;
}

.isexpanded ~ ul {
 display: none;
}

.isexpanded:checked ~ ul {
 display: block;
}



.isexpanded2 {
  display: none;
}

.isexpanded2 ~ #errors {
 display: none;
}

.isexpanded2:checked ~ #errors {
 display: block;
}

.isexpanded3 {
  display: none;
}

.isexpanded3 ~ #logs {
 display: none;
}

.isexpanded3:checked ~ #logs {
 display: block;
}


label { cursor: pointer; }

label:hover {
   text-decoration: underline;
}

</style>
</head>
<body>
<!-- REPLACE_ME -->
</body>
</html>