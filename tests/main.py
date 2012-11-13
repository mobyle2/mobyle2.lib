import unittest


def allTests():
    from testData import TestDataType
    from testData import TestDataFormat
    from testData import TestData
    from testData import TestStructData
    from testData import TestCollectionData
    

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDataType))
    suite.addTest(unittest.makeSuite(TestDataFormat))
    suite.addTest(unittest.makeSuite(TestData))
    suite.addTest(unittest.makeSuite(TestStructData))
    suite.addTest(unittest.makeSuite(TestCollectionData))

    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(allTests())