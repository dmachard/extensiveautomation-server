
import Dict2Xml
import Xml2Dict

codecD2X = Dict2Xml.Dict2Xml( coding = None )

pl = { 'steps': { 'step': 
    
    [
        {
            u'expected': {'type': 'string', 'value': u'fsd'},
            u'summary': {'type': 'string', 'value': u'fds'},
            'id': "1",
            u'description': {'type': 'string', 'value': u'fds'}
        },

        {
            u'expected': {'type': 'string', 'value': u'fsd'},
            u'summary': {'type': 'string', 'value': u'fds'},
            'id': "1",
            u'description': {'type': 'string', 'value': u'fds'}
        }
    ]

    }
    }
retD2X = codecD2X.parseDict( dico = pl )
print retD2X