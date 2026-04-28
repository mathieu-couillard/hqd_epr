
# Single QUA script generated at 2025-06-09 09:58:45.629163
# QUA library version: 1.1.1

from qm.qua import *

with program() as prog:
    v1 = declare(int, )
    v2 = declare(int, )
    a1 = declare(fixed, size=1000)
    a2 = declare(fixed, size=1000)
    a3 = declare(fixed, size=1000)
    a4 = declare(fixed, size=1000)
    a5 = declare(fixed, size=1000)
    a6 = declare(fixed, size=1000)
    with for_(v1,0,(v1<1),(v1+1)):
        align()
        reset_phase("spin")
        reset_phase("digitizer")
        reset_frame("spin")
        atr_r3 = declare_stream(adc_trace=True)
        measure("readout", "digitizer", atr_r3, demod.sliced("cos", a3, 1, "out1"), demod.sliced("sin", a5, 1, "out1"), demod.sliced("cos", a6, 1, "out2"), demod.sliced("sin", a4, 1, "out2"))
        play("spa", "SPA")
        play("x90", "spin")
        wait(250, "spin")
        frame_rotation_2pi(0.5, "spin")
        play("x180", "spin")
        wait(200, "spin")
        align("spin", "CryoSw")
        with for_(v2,0,(v2<1000),(v2+1)):
            assign(a1[v2], (a3[v2]+a4[v2]))
            assign(a2[v2], (a5[v2]-a6[v2]))
            r1 = declare_stream()
            save(a1[v2], r1)
            r2 = declare_stream()
            save(a2[v2], r2)
        r4 = declare_stream()
        save(v1, r4)
    with stream_processing():
        r1.buffer(1000).average().save("I")
        r2.buffer(1000).average().save("Q")
        r4.save("Iteration")



####     SERIALIZATION WAS NOT COMPLETE     ####
#
#  Original   {  "config": {},  "script": {    "variables": [      {        "name": "v1",        "size": 1      },      {        "name": "v2",        "size": 1      },      {        "name": "a1",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a2",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a3",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a4",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a5",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a6",        "type": "REAL",        "size": 1000,        "dim": 1      }    ],    "body": {      "statements": [        {          "for": {            "init": {              "statements": [                {                  "assign": {                    "expression": {                      "literal": {                        "value": "0",                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "condition": {              "binaryOperation": {                "op": "LT",                "left": {                  "variable": {                    "name": "v1",                    "loc": "stripped"                  }                },                "right": {                  "literal": {                    "value": "1",                    "loc": "stripped"                  }                },                "loc": "stripped"              }            },            "update": {              "statements": [                {                  "assign": {                    "expression": {                      "binaryOperation": {                        "left": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "body": {              "statements": [                {                  "align": {                    "loc": "stripped"                  }                },                {                  "resetPhase": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    }                  }                },                {                  "resetPhase": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "digitizer"                    }                  }                },                {                  "resetFrame": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    }                  }                },                {                  "measure": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "digitizer"                    },                    "pulse": {                      "loc": "stripped",                      "name": "readout"                    },                    "streamAs": "atr_r3",                    "measureProcesses": [                      {                        "analog": {                          "loc": "stripped",                          "demodIntegration": {                            "integration": {                              "loc": "stripped",                              "name": "cos"                            },                            "target": {                              "loc": "stripped",                              "vectorProcess": {                                "array": {                                  "name": "a3",                                  "loc": "stripped"                                },                                "timeDivision": {                                  "sliced": {                                    "loc": "stripped",                                    "samplesPerChunk": 1                                  }                                }                              }                            },                            "elementOutput": "out1"                          }                        }                      },                      {                        "analog": {                          "loc": "stripped",                          "demodIntegration": {                            "integration": {                              "loc": "stripped",                              "name": "sin"                            },                            "target": {                              "loc": "stripped",                              "vectorProcess": {                                "array": {                                  "name": "a5",                                  "loc": "stripped"                                },                                "timeDivision": {                                  "sliced": {                                    "loc": "stripped",                                    "samplesPerChunk": 1                                  }                                }                              }                            },                            "elementOutput": "out1"                          }                        }                      },                      {                        "analog": {                          "loc": "stripped",                          "demodIntegration": {                            "integration": {                              "loc": "stripped",                              "name": "cos"                            },                            "target": {                              "loc": "stripped",                              "vectorProcess": {                                "array": {                                  "name": "a6",                                  "loc": "stripped"                                },                                "timeDivision": {                                  "sliced": {                                    "loc": "stripped",                                    "samplesPerChunk": 1                                  }                                }                              }                            },                            "elementOutput": "out2"                          }                        }                      },                      {                        "analog": {                          "loc": "stripped",                          "demodIntegration": {                            "integration": {                              "loc": "stripped",                              "name": "sin"                            },                            "target": {                              "loc": "stripped",                              "vectorProcess": {                                "array": {                                  "name": "a4",                                  "loc": "stripped"                                },                                "timeDivision": {                                  "sliced": {                                    "loc": "stripped",                                    "samplesPerChunk": 1                                  }                                }                              }                            },                            "elementOutput": "out2"                          }                        }                      }                    ]                  }                },                {                  "play": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "SPA"                    },                    "namedPulse": {                      "loc": "stripped",                      "name": "spa"                    }                  }                },                {                  "play": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    },                    "namedPulse": {                      "loc": "stripped",                      "name": "x90"                    }                  }                },                {                  "wait": {                    "loc": "stripped",                    "qe": [                      {                        "loc": "stripped",                        "name": "spin"                      }                    ],                    "time": {                      "literal": {                        "value": "250",                        "loc": "stripped"                      }                    }                  }                },                {                  "zRotation": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    },                    "value": {                      "literal": {                        "value": "0.5",                        "type": "REAL",                        "loc": "stripped"                      }                    }                  }                },                {                  "play": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    },                    "namedPulse": {                      "loc": "stripped",                      "name": "x180"                    }                  }                },                {                  "wait": {                    "loc": "stripped",                    "qe": [                      {                        "loc": "stripped",                        "name": "spin"                      }                    ],                    "time": {                      "literal": {                        "value": "200",                        "loc": "stripped"                      }                    }                  }                },                {                  "align": {                    "loc": "stripped",                    "qe": [                      {                        "loc": "stripped",                        "name": "spin"                      },                      {                        "loc": "stripped",                        "name": "CryoSw"                      }                    ]                  }                },                {                  "for": {                    "init": {                      "statements": [                        {                          "assign": {                            "expression": {                              "literal": {                                "value": "0",                                "loc": "stripped"                              }                            },                            "target": {                              "variable": {                                "name": "v2",                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        }                      ]                    },                    "condition": {                      "binaryOperation": {                        "op": "LT",                        "left": {                          "variable": {                            "name": "v2",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1000",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "update": {                      "statements": [                        {                          "assign": {                            "expression": {                              "binaryOperation": {                                "left": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "right": {                                  "literal": {                                    "value": "1",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "target": {                              "variable": {                                "name": "v2",                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        }                      ]                    },                    "body": {                      "statements": [                        {                          "assign": {                            "expression": {                              "binaryOperation": {                                "left": {                                  "arrayCell": {                                    "arrayVar": {                                      "name": "a3",                                      "loc": "stripped"                                    },                                    "index": {                                      "variable": {                                        "name": "v2",                                        "loc": "stripped"                                      }                                    },                                    "loc": "stripped"                                  }                                },                                "right": {                                  "arrayCell": {                                    "arrayVar": {                                      "name": "a4",                                      "loc": "stripped"                                    },                                    "index": {                                      "variable": {                                        "name": "v2",                                        "loc": "stripped"                                      }                                    },                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "target": {                              "arrayCell": {                                "arrayVar": {                                  "name": "a1",                                  "loc": "stripped"                                },                                "index": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        },                        {                          "assign": {                            "expression": {                              "binaryOperation": {                                "op": "SUB",                                "left": {                                  "arrayCell": {                                    "arrayVar": {                                      "name": "a5",                                      "loc": "stripped"                                    },                                    "index": {                                      "variable": {                                        "name": "v2",                                        "loc": "stripped"                                      }                                    },                                    "loc": "stripped"                                  }                                },                                "right": {                                  "arrayCell": {                                    "arrayVar": {                                      "name": "a6",                                      "loc": "stripped"                                    },                                    "index": {                                      "variable": {                                        "name": "v2",                                        "loc": "stripped"                                      }                                    },                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "target": {                              "arrayCell": {                                "arrayVar": {                                  "name": "a2",                                  "loc": "stripped"                                },                                "index": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        },                        {                          "save": {                            "tag": "r1",                            "source": {                              "arrayCell": {                                "arrayVar": {                                  "name": "a1",                                  "loc": "stripped"                                },                                "index": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        },                        {                          "save": {                            "tag": "r2",                            "source": {                              "arrayCell": {                                "arrayVar": {                                  "name": "a2",                                  "loc": "stripped"                                },                                "index": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        }                      ]                    },                    "loc": "stripped"                  }                },                {                  "save": {                    "tag": "r4",                    "source": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "loc": "stripped"          }        }      ]    }  },  "resultAnalysis": {    "model": [      {        "values": [          {            "stringValue": "save"          },          {            "stringValue": "I"          },          {            "listValue": {              "values": [                {                  "stringValue": "average"                },                {                  "listValue": {                    "values": [                      {                        "stringValue": "buffer"                      },                      {                        "stringValue": "1000"                      },                      {                        "listValue": {                          "values": [                            {                              "stringValue": "@re"                            },                            {                              "stringValue": "0"                            },                            {                              "stringValue": "r1"                            }                          ]                        }                      }                    ]                  }                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "save"          },          {            "stringValue": "Q"          },          {            "listValue": {              "values": [                {                  "stringValue": "average"                },                {                  "listValue": {                    "values": [                      {                        "stringValue": "buffer"                      },                      {                        "stringValue": "1000"                      },                      {                        "listValue": {                          "values": [                            {                              "stringValue": "@re"                            },                            {                              "stringValue": "0"                            },                            {                              "stringValue": "r2"                            }                          ]                        }                      }                    ]                  }                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "save"          },          {            "stringValue": "Iteration"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r4"                }              ]            }          }        ]      }    ]  }}
#  Serialized {  "config": {},  "script": {    "variables": [      {        "name": "v1",        "size": 1      },      {        "name": "v2",        "size": 1      },      {        "name": "a1",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a2",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a3",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a4",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a5",        "type": "REAL",        "size": 1000,        "dim": 1      },      {        "name": "a6",        "type": "REAL",        "size": 1000,        "dim": 1      }    ],    "body": {      "statements": [        {          "for": {            "init": {              "statements": [                {                  "assign": {                    "expression": {                      "literal": {                        "value": "0",                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "condition": {              "binaryOperation": {                "op": "LT",                "left": {                  "variable": {                    "name": "v1",                    "loc": "stripped"                  }                },                "right": {                  "literal": {                    "value": "1",                    "loc": "stripped"                  }                },                "loc": "stripped"              }            },            "update": {              "statements": [                {                  "assign": {                    "expression": {                      "binaryOperation": {                        "left": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "body": {              "statements": [                {                  "align": {                    "loc": "stripped"                  }                },                {                  "resetPhase": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    }                  }                },                {                  "resetPhase": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "digitizer"                    }                  }                },                {                  "resetFrame": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    }                  }                },                {                  "measure": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "digitizer"                    },                    "pulse": {                      "loc": "stripped",                      "name": "readout"                    },                    "streamAs": "atr_r1",                    "measureProcesses": [                      {                        "analog": {                          "loc": "stripped",                          "demodIntegration": {                            "integration": {                              "loc": "stripped",                              "name": "cos"                            },                            "target": {                              "loc": "stripped",                              "vectorProcess": {                                "array": {                                  "name": "a3",                                  "loc": "stripped"                                },                                "timeDivision": {                                  "sliced": {                                    "loc": "stripped",                                    "samplesPerChunk": 1                                  }                                }                              }                            },                            "elementOutput": "out1"                          }                        }                      },                      {                        "analog": {                          "loc": "stripped",                          "demodIntegration": {                            "integration": {                              "loc": "stripped",                              "name": "sin"                            },                            "target": {                              "loc": "stripped",                              "vectorProcess": {                                "array": {                                  "name": "a5",                                  "loc": "stripped"                                },                                "timeDivision": {                                  "sliced": {                                    "loc": "stripped",                                    "samplesPerChunk": 1                                  }                                }                              }                            },                            "elementOutput": "out1"                          }                        }                      },                      {                        "analog": {                          "loc": "stripped",                          "demodIntegration": {                            "integration": {                              "loc": "stripped",                              "name": "cos"                            },                            "target": {                              "loc": "stripped",                              "vectorProcess": {                                "array": {                                  "name": "a6",                                  "loc": "stripped"                                },                                "timeDivision": {                                  "sliced": {                                    "loc": "stripped",                                    "samplesPerChunk": 1                                  }                                }                              }                            },                            "elementOutput": "out2"                          }                        }                      },                      {                        "analog": {                          "loc": "stripped",                          "demodIntegration": {                            "integration": {                              "loc": "stripped",                              "name": "sin"                            },                            "target": {                              "loc": "stripped",                              "vectorProcess": {                                "array": {                                  "name": "a4",                                  "loc": "stripped"                                },                                "timeDivision": {                                  "sliced": {                                    "loc": "stripped",                                    "samplesPerChunk": 1                                  }                                }                              }                            },                            "elementOutput": "out2"                          }                        }                      }                    ]                  }                },                {                  "play": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "SPA"                    },                    "namedPulse": {                      "loc": "stripped",                      "name": "spa"                    }                  }                },                {                  "play": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    },                    "namedPulse": {                      "loc": "stripped",                      "name": "x90"                    }                  }                },                {                  "wait": {                    "loc": "stripped",                    "qe": [                      {                        "loc": "stripped",                        "name": "spin"                      }                    ],                    "time": {                      "literal": {                        "value": "250",                        "loc": "stripped"                      }                    }                  }                },                {                  "zRotation": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    },                    "value": {                      "literal": {                        "value": "0.5",                        "type": "REAL",                        "loc": "stripped"                      }                    }                  }                },                {                  "play": {                    "loc": "stripped",                    "qe": {                      "loc": "stripped",                      "name": "spin"                    },                    "namedPulse": {                      "loc": "stripped",                      "name": "x180"                    }                  }                },                {                  "wait": {                    "loc": "stripped",                    "qe": [                      {                        "loc": "stripped",                        "name": "spin"                      }                    ],                    "time": {                      "literal": {                        "value": "200",                        "loc": "stripped"                      }                    }                  }                },                {                  "align": {                    "loc": "stripped",                    "qe": [                      {                        "loc": "stripped",                        "name": "spin"                      },                      {                        "loc": "stripped",                        "name": "CryoSw"                      }                    ]                  }                },                {                  "for": {                    "init": {                      "statements": [                        {                          "assign": {                            "expression": {                              "literal": {                                "value": "0",                                "loc": "stripped"                              }                            },                            "target": {                              "variable": {                                "name": "v2",                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        }                      ]                    },                    "condition": {                      "binaryOperation": {                        "op": "LT",                        "left": {                          "variable": {                            "name": "v2",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1000",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "update": {                      "statements": [                        {                          "assign": {                            "expression": {                              "binaryOperation": {                                "left": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "right": {                                  "literal": {                                    "value": "1",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "target": {                              "variable": {                                "name": "v2",                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        }                      ]                    },                    "body": {                      "statements": [                        {                          "assign": {                            "expression": {                              "binaryOperation": {                                "left": {                                  "arrayCell": {                                    "arrayVar": {                                      "name": "a3",                                      "loc": "stripped"                                    },                                    "index": {                                      "variable": {                                        "name": "v2",                                        "loc": "stripped"                                      }                                    },                                    "loc": "stripped"                                  }                                },                                "right": {                                  "arrayCell": {                                    "arrayVar": {                                      "name": "a4",                                      "loc": "stripped"                                    },                                    "index": {                                      "variable": {                                        "name": "v2",                                        "loc": "stripped"                                      }                                    },                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "target": {                              "arrayCell": {                                "arrayVar": {                                  "name": "a1",                                  "loc": "stripped"                                },                                "index": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        },                        {                          "assign": {                            "expression": {                              "binaryOperation": {                                "op": "SUB",                                "left": {                                  "arrayCell": {                                    "arrayVar": {                                      "name": "a5",                                      "loc": "stripped"                                    },                                    "index": {                                      "variable": {                                        "name": "v2",                                        "loc": "stripped"                                      }                                    },                                    "loc": "stripped"                                  }                                },                                "right": {                                  "arrayCell": {                                    "arrayVar": {                                      "name": "a6",                                      "loc": "stripped"                                    },                                    "index": {                                      "variable": {                                        "name": "v2",                                        "loc": "stripped"                                      }                                    },                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "target": {                              "arrayCell": {                                "arrayVar": {                                  "name": "a2",                                  "loc": "stripped"                                },                                "index": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        },                        {                          "save": {                            "tag": "r2",                            "source": {                              "arrayCell": {                                "arrayVar": {                                  "name": "a1",                                  "loc": "stripped"                                },                                "index": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        },                        {                          "save": {                            "tag": "r3",                            "source": {                              "arrayCell": {                                "arrayVar": {                                  "name": "a2",                                  "loc": "stripped"                                },                                "index": {                                  "variable": {                                    "name": "v2",                                    "loc": "stripped"                                  }                                },                                "loc": "stripped"                              }                            },                            "loc": "stripped"                          }                        }                      ]                    },                    "loc": "stripped"                  }                },                {                  "save": {                    "tag": "r4",                    "source": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "loc": "stripped"          }        }      ]    }  },  "resultAnalysis": {    "model": [      {        "values": [          {            "stringValue": "save"          },          {            "stringValue": "I"          },          {            "listValue": {              "values": [                {                  "stringValue": "average"                },                {                  "listValue": {                    "values": [                      {                        "stringValue": "buffer"                      },                      {                        "stringValue": "1000"                      },                      {                        "listValue": {                          "values": [                            {                              "stringValue": "@re"                            },                            {                              "stringValue": "0"                            },                            {                              "stringValue": "r2"                            }                          ]                        }                      }                    ]                  }                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "save"          },          {            "stringValue": "Q"          },          {            "listValue": {              "values": [                {                  "stringValue": "average"                },                {                  "listValue": {                    "values": [                      {                        "stringValue": "buffer"                      },                      {                        "stringValue": "1000"                      },                      {                        "listValue": {                          "values": [                            {                              "stringValue": "@re"                            },                            {                              "stringValue": "0"                            },                            {                              "stringValue": "r3"                            }                          ]                        }                      }                    ]                  }                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "save"          },          {            "stringValue": "Iteration"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r4"                }              ]            }          }        ]      }    ]  }}
#
################################################

        
config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.021664633363113018,
                    "delay": 200,
                },
                "2": {
                    "offset": -0.020055943976947946,
                    "delay": 200,
                },
            },
            "digital_outputs": {
                "1": {},
                "2": {},
                "3": {},
                "6": {},
                "5": {},
            },
            "analog_inputs": {
                "1": {
                    "offset": -0.01,
                    "gain_db": 0,
                },
                "2": {
                    "offset": -0.01,
                    "gain_db": 0,
                },
            },
        },
    },
    "elements": {
        "spin": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4480887500.0,
                "mixer": "mixer_spin1",
            },
            "intermediate_frequency": 100000000.0,
            "operations": {
                "saturation": "saturation_pulse",
                "pi": "pi_pulse",
                "pi_half": "pi_half_pulse",
                "gaussian": "gaussian_pulse",
                "x90": "x90-pulse",
                "x180": "x180-pulse",
                "-x90": "-x90-pulse",
                "y90": "y90-pulse",
                "y180": "y180-pulse",
                "-y90": "-y90-pulse",
            },
            "digitalInputs": {
                "RT_SW": {
                    "port": ('con1', 6),
                    "delay": 332,
                    "buffer": 180,
                },
            },
        },
        "laser": {
            "digitalInputs": {
                "marker": {
                    "port": ('con1', 1),
                    "delay": 0,
                    "buffer": 0.0,
                },
            },
            "operations": {
                "initialize": "initialization_pulse",
                "readout_odmr": "readout_odmr_pulse",
            },
        },
        "digitizer": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4480887500.0,
                "mixer": "mixer_spin2",
            },
            "intermediate_frequency": 100000000.0,
            "operations": {
                "readout": "readout_pulse",
            },
            "digitalInputs": {
                "marker": {
                    "port": ('con1', 5),
                    "delay": 24,
                    "buffer": 0,
                },
            },
            "time_of_flight": 24,
            "smearing": 0,
            "outputs": {
                "out1": ('con1', 1),
                "out2": ('con1', 2),
            },
        },
        "CryoSw": {
            "digitalInputs": {
                "marker": {
                    "port": ('con1', 2),
                    "delay": 0,
                    "buffer": 0,
                },
            },
            "operations": {
                "cryosw": "cryosw_on",
            },
        },
        "SPA": {
            "digitalInputs": {
                "marker": {
                    "port": ('con1', 3),
                    "delay": 0,
                    "buffer": 0.0,
                },
            },
            "operations": {
                "spa": "spa_on",
            },
        },
    },
    "pulses": {
        "sq": {
            "operation": "control",
            "length": 400,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "saturation_pulse": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "pi_half_pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "pi_half_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "pi_pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "pi_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "gaussian_pulse": {
            "operation": "control",
            "length": 400,
            "waveforms": {
                "I": "gaussian_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "x90-pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "pi_half_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "x180-pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "pi_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "-x90-pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "minus_pi_half_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "y90-pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "pi_half_wf",
            },
            "digital_marker": "ON",
        },
        "y180-pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "pi_wf",
            },
            "digital_marker": "ON",
        },
        "-y90-pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "minus_pi_half_wf",
            },
            "digital_marker": "ON",
        },
        "readout_pulse": {
            "operation": "measurement",
            "length": 4000,
            "waveforms": {
                "I": "zero_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_weights",
                "sin": "sin_weights",
                "minus_sin": "minus_sin_weights",
            },
        },
        "initialization_pulse": {
            "operation": "control",
            "length": 40,
            "digital_marker": "LASER_ON",
        },
        "readout_odmr_pulse": {
            "operation": "control",
            "length": 4000,
            "digital_marker": "LASER_ON",
        },
        "cryosw_on": {
            "operation": "control",
            "length": 4500,
            "digital_marker": "ON",
        },
        "spa_on": {
            "operation": "control",
            "length": 4000,
            "digital_marker": "spa_trigger",
        },
    },
    "waveforms": {
        "const_wf": {
            "type": "constant",
            "sample": 0.5,
        },
        "gaussian_wf": {
            "type": "arbitrary",
            "samples": [0.022313984000894595, 0.02301870893368783, 0.023741980663118722, 0.02448415239337985, 0.025245579401142696, 0.026026618874865563, 0.026827629747575098, 0.027648972523077443, 0.028491009095561355, 0.029354102562561588, 0.03023861703125707, 0.031144917418085637, 0.032073369241662965, 0.033024338409001514, 0.03399819099503172, 0.03499529301543567, 0.036016010192810914, 0.03706070771619045, 0.03812974999395229, 0.03922350040016129, 0.04034232101439346, 0.04148657235510257, 0.042656613106597054, 0.04385279983970452, 0.04507548672621055, 0.04632502524716747, 0.047601763895178506, 0.04890604787077224, 0.05023821877299224, 0.051598614284336215, 0.05298756785018939, 0.05440540835290671, 0.055852459780708456, 0.05732904089156428, 0.05883546487225093, 0.06037203899277868, 0.061939064256393075, 0.0635368350453669, 0.06516563876280997, 0.06682575547073258, 0.06851745752461019, 0.07024100920470605, 0.07199666634441962, 0.07378467595593799, 0.07560527585347775, 0.07745869427441475, 0.07934514949860864, 0.0812648494662392, 0.08321799139448006, 0.08520476139334576, 0.08722533408105593, 0.08927987219927043, 0.09136852622855698, 0.09349143400446146, 0.09564872033455936, 0.09784049661687437, 0.1000668604600577, 0.10232789530572876, 0.10462367005338497, 0.1069542386882945, 0.10931963991279237, 0.11171989678140519, 0.11415501634023631, 0.11662498927104675, 0.11912978954047254, 0.12166937405482284, 0.12424368232090653, 0.12685263611333797, 0.12949613914877553, 0.1321740767675477, 0.13488631562312384, 0.13763270337988676, 0.14041306841966547, 0.14322721955748519, 0.14607494576699184, 0.14895601591600616, 0.151870178512661, 0.15481716146257238, 0.1577966718374916, 0.16080839565588248, 0.1638519976758621, 0.16692712120093964, 0.17003338789898062, 0.17317039763481878, 0.1763377283169297, 0.17953493575857307, 0.1827615535538016, 0.1860170929687262, 0.18930104284841642, 0.1926128695398053, 0.19595201683095684, 0.19931790590704201, 0.2027099353233575, 0.20612748099570785, 0.2095698962084588, 0.2130365116405542, 0.2165266354097755, 0.2200395531355059, 0.22357452802024683, 0.22713080095011554, 0.2307075906145385, 0.2343040936453342, 0.2379194847753636, 0.24155291701690568, 0.24520352185989758, 0.24887040949015815, 0.25255266902769424, 0.25624936878516824, 0.25995955654658376, 0.26368225986622607, 0.26741648638787124, 0.27116122418425553, 0.2749154421167759, 0.2786780902153669, 0.28244810007848004, 0.2862243852930639, 0.29000584187442463, 0.29379134872581925, 0.29757976811761266, 0.3013699461858041, 0.3051607134497058, 0.3089508853485331, 0.3127392627966391, 0.31652463275710657, 0.3203057688333823, 0.3240814318786186, 0.3278503706223609, 0.3316113223141977, 0.3353630133839666, 0.33910416011808525, 0.34283346935155606, 0.3465496391751689, 0.3502513596574042, 0.35393731358051944, 0.3576061771902768, 0.3612566209587533, 0.3648873103596508, 0.36849690665550544, 0.3720840676961773, 0.37564744872797906, 0.3791857032127895, 0.38269748365647566, 0.3861814424459327, 0.3896362326940359, 0.39306050909178, 0.39645292876687066, 0.39981215214801763, 0.403136843834164, 0.4064256734678781, 0.4096773166121201, 0.4128904556295857, 0.41606378056382193, 0.41919599002129804, 0.42228579205361055, 0.4253319050389923, 0.42833305856229176, 0.4312879942925826, 0.4341954668575614, 0.43705424471388854, 0.4398631110126247, 0.44262086445891713, 0.44532632016508844, 0.44797831049628406, 0.45057568590783603, 0.4531173157735052, 0.45560208920376954, 0.4580289158533306, 0.4603967267170193, 0.4627044749132883, 0.4649511364544897, 0.46713571100314455, 0.4692572226134244, 0.47131472045707595, 0.4733072795330334, 0.4752340013599784, 0.47709401465112145, 0.4788864759704969, 0.48061057037007826, 0.4822655120070424, 0.48385054474052613, 0.48536494270724323, 0.4868080108753469, 0.4881790855759471, 0.48947753501171326, 0.4907027597420176, 0.4918541931440967, 0.4929313018497351, 0.49393358615700017, 0.49486058041658254, 0.4957118533923249, 0.4964870085955472, 0.497185684592807, 0.49780755528675896, 0.498352330169809, 0.4988197545502864, 0.49920960975088746, 0.4995217132791747, 0.4997559189699447, 0.4999121170993094] + [0.49999023447036683] * 2 + [0.4999121170993094, 0.4997559189699447, 0.4995217132791747, 0.49920960975088746, 0.4988197545502864, 0.498352330169809, 0.49780755528675896, 0.497185684592807, 0.4964870085955472, 0.4957118533923249, 0.49486058041658254, 0.49393358615700017, 0.4929313018497351, 0.4918541931440967, 0.4907027597420176, 0.48947753501171326, 0.4881790855759471, 0.4868080108753469, 0.48536494270724323, 0.48385054474052613, 0.4822655120070424, 0.48061057037007826, 0.4788864759704969, 0.47709401465112145, 0.4752340013599784, 0.4733072795330334, 0.47131472045707595, 0.4692572226134244, 0.46713571100314455, 0.4649511364544897, 0.4627044749132883, 0.4603967267170193, 0.4580289158533306, 0.45560208920376954, 0.4531173157735052, 0.45057568590783603, 0.44797831049628406, 0.44532632016508844, 0.44262086445891713, 0.4398631110126247, 0.43705424471388854, 0.4341954668575614, 0.4312879942925826, 0.42833305856229176, 0.4253319050389923, 0.42228579205361055, 0.41919599002129804, 0.41606378056382193, 0.4128904556295857, 0.4096773166121201, 0.4064256734678781, 0.403136843834164, 0.39981215214801763, 0.39645292876687066, 0.39306050909178, 0.3896362326940359, 0.3861814424459327, 0.38269748365647566, 0.3791857032127895, 0.37564744872797906, 0.3720840676961773, 0.36849690665550544, 0.3648873103596508, 0.3612566209587533, 0.3576061771902768, 0.35393731358051944, 0.3502513596574042, 0.3465496391751689, 0.34283346935155606, 0.33910416011808525, 0.3353630133839666, 0.3316113223141977, 0.3278503706223609, 0.3240814318786186, 0.3203057688333823, 0.31652463275710657, 0.3127392627966391, 0.3089508853485331, 0.3051607134497058, 0.3013699461858041, 0.29757976811761266, 0.29379134872581925, 0.29000584187442463, 0.2862243852930639, 0.28244810007848004, 0.2786780902153669, 0.2749154421167759, 0.27116122418425553, 0.26741648638787124, 0.26368225986622607, 0.25995955654658376, 0.25624936878516824, 0.25255266902769424, 0.24887040949015815, 0.24520352185989758, 0.24155291701690568, 0.2379194847753636, 0.2343040936453342, 0.2307075906145385, 0.22713080095011554, 0.22357452802024683, 0.2200395531355059, 0.2165266354097755, 0.2130365116405542, 0.2095698962084588, 0.20612748099570785, 0.2027099353233575, 0.19931790590704201, 0.19595201683095684, 0.1926128695398053, 0.18930104284841642, 0.1860170929687262, 0.1827615535538016, 0.17953493575857307, 0.1763377283169297, 0.17317039763481878, 0.17003338789898062, 0.16692712120093964, 0.1638519976758621, 0.16080839565588248, 0.1577966718374916, 0.15481716146257238, 0.151870178512661, 0.14895601591600616, 0.14607494576699184, 0.14322721955748519, 0.14041306841966547, 0.13763270337988676, 0.13488631562312384, 0.1321740767675477, 0.12949613914877553, 0.12685263611333797, 0.12424368232090653, 0.12166937405482284, 0.11912978954047254, 0.11662498927104675, 0.11415501634023631, 0.11171989678140519, 0.10931963991279237, 0.1069542386882945, 0.10462367005338497, 0.10232789530572876, 0.1000668604600577, 0.09784049661687437, 0.09564872033455936, 0.09349143400446146, 0.09136852622855698, 0.08927987219927043, 0.08722533408105593, 0.08520476139334576, 0.08321799139448006, 0.0812648494662392, 0.07934514949860864, 0.07745869427441475, 0.07560527585347775, 0.07378467595593799, 0.07199666634441962, 0.07024100920470605, 0.06851745752461019, 0.06682575547073258, 0.06516563876280997, 0.0635368350453669, 0.061939064256393075, 0.06037203899277868, 0.05883546487225093, 0.05732904089156428, 0.055852459780708456, 0.05440540835290671, 0.05298756785018939, 0.051598614284336215, 0.05023821877299224, 0.04890604787077224, 0.047601763895178506, 0.04632502524716747, 0.04507548672621055, 0.04385279983970452, 0.042656613106597054, 0.04148657235510257, 0.04034232101439346, 0.03922350040016129, 0.03812974999395229, 0.03706070771619045, 0.036016010192810914, 0.03499529301543567, 0.03399819099503172, 0.033024338409001514, 0.032073369241662965, 0.031144917418085637, 0.03023861703125707, 0.029354102562561588, 0.028491009095561355, 0.027648972523077443, 0.026827629747575098, 0.026026618874865563, 0.025245579401142696, 0.02448415239337985, 0.023741980663118722, 0.02301870893368783, 0.022313984000894595],
        },
        "pi_wf": {
            "type": "constant",
            "sample": 0.5,
        },
        "pi_half_wf": {
            "type": "constant",
            "sample": 0.25,
        },
        "minus_pi_half_wf": {
            "type": "constant",
            "sample": -0.25,
        },
        "zero_wf": {
            "type": "constant",
            "sample": 0,
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [(1, 0)],
        },
        "OFF": {
            "samples": [(0, 0)],
        },
        "spa_trigger": {
            "samples": [(1, 0)],
        },
        "LASER_ON": {
            "samples": [(1, 0)],
        },
    },
    "integration_weights": {
        "cos_weights": {
            "cosine": [(1.0, 4000)],
            "sine": [(0.0, 4000)],
        },
        "sin_weights": {
            "cosine": [(0.0, 4000)],
            "sine": [(1.0, 4000)],
        },
        "minus_sin_weights": {
            "cosine": [(0.0, 4000)],
            "sine": [(-1.0, 4000)],
        },
    },
    "mixers": {
        "mixer_spin1": [{'intermediate_frequency': 100000000.0, 'lo_frequency': 4480887500.0, 'correction': [1.0, 0.0, 0.0, 1.0]}],
        "mixer_spin2": [{'intermediate_frequency': 100000000.0, 'lo_frequency': 4480887500.0, 'correction': [1.0, 0.0, 0.0, 1.0]}],
    },
}

loaded_config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.021664633363113018,
                    "delay": 200,
                    "shareable": False,
                },
                "2": {
                    "offset": -0.020055943976947946,
                    "delay": 200,
                    "shareable": False,
                },
            },
            "analog_inputs": {
                "1": {
                    "offset": -0.01,
                    "gain_db": 0,
                    "shareable": False,
                },
                "2": {
                    "offset": -0.01,
                    "gain_db": 0,
                    "shareable": False,
                },
            },
            "digital_outputs": {
                "1": {
                    "shareable": False,
                },
                "2": {
                    "shareable": False,
                },
                "3": {
                    "shareable": False,
                },
                "6": {
                    "shareable": False,
                },
                "5": {
                    "shareable": False,
                },
            },
        },
    },
    "oscillators": {},
    "elements": {
        "spin": {
            "digitalInputs": {
                "RT_SW": {
                    "delay": 332,
                    "buffer": 180,
                    "port": ('con1', 6),
                },
            },
            "digitalOutputs": {},
            "intermediate_frequency": 100000000.0,
            "operations": {
                "saturation": "saturation_pulse",
                "pi": "pi_pulse",
                "pi_half": "pi_half_pulse",
                "gaussian": "gaussian_pulse",
                "x90": "x90-pulse",
                "x180": "x180-pulse",
                "-x90": "-x90-pulse",
                "y90": "y90-pulse",
                "y180": "y180-pulse",
                "-y90": "-y90-pulse",
            },
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "mixer": "mixer_spin1",
                "lo_frequency": 4480887500.0,
            },
        },
        "laser": {
            "digitalInputs": {
                "marker": {
                    "delay": 0,
                    "buffer": 0,
                    "port": ('con1', 1),
                },
            },
            "digitalOutputs": {},
            "operations": {
                "initialize": "initialization_pulse",
                "readout_odmr": "readout_odmr_pulse",
            },
        },
        "digitizer": {
            "digitalInputs": {
                "marker": {
                    "delay": 24,
                    "buffer": 0,
                    "port": ('con1', 5),
                },
            },
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con1', 1),
                "out2": ('con1', 2),
            },
            "time_of_flight": 24,
            "smearing": 0,
            "intermediate_frequency": 100000000.0,
            "operations": {
                "readout": "readout_pulse",
            },
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "mixer": "mixer_spin2",
                "lo_frequency": 4480887500.0,
            },
        },
        "CryoSw": {
            "digitalInputs": {
                "marker": {
                    "delay": 0,
                    "buffer": 0,
                    "port": ('con1', 2),
                },
            },
            "digitalOutputs": {},
            "operations": {
                "cryosw": "cryosw_on",
            },
        },
        "SPA": {
            "digitalInputs": {
                "marker": {
                    "delay": 0,
                    "buffer": 0,
                    "port": ('con1', 3),
                },
            },
            "digitalOutputs": {},
            "operations": {
                "spa": "spa_on",
            },
        },
    },
    "pulses": {
        "sq": {
            "length": 400,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "saturation_pulse": {
            "length": 500,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "pi_half_pulse": {
            "length": 100,
            "waveforms": {
                "I": "pi_half_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "pi_pulse": {
            "length": 100,
            "waveforms": {
                "I": "pi_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "gaussian_pulse": {
            "length": 400,
            "waveforms": {
                "I": "gaussian_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "x90-pulse": {
            "length": 100,
            "waveforms": {
                "I": "pi_half_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "x180-pulse": {
            "length": 100,
            "waveforms": {
                "I": "pi_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "-x90-pulse": {
            "length": 100,
            "waveforms": {
                "I": "minus_pi_half_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "y90-pulse": {
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "pi_half_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "y180-pulse": {
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "pi_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "-y90-pulse": {
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "minus_pi_half_wf",
            },
            "digital_marker": "ON",
            "operation": "control",
        },
        "readout_pulse": {
            "length": 4000,
            "waveforms": {
                "I": "zero_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_weights",
                "sin": "sin_weights",
                "minus_sin": "minus_sin_weights",
            },
            "operation": "measurement",
        },
        "initialization_pulse": {
            "length": 40,
            "digital_marker": "LASER_ON",
            "operation": "control",
        },
        "readout_odmr_pulse": {
            "length": 4000,
            "digital_marker": "LASER_ON",
            "operation": "control",
        },
        "cryosw_on": {
            "length": 4500,
            "digital_marker": "ON",
            "operation": "control",
        },
        "spa_on": {
            "length": 4000,
            "digital_marker": "spa_trigger",
            "operation": "control",
        },
    },
    "waveforms": {
        "const_wf": {
            "sample": 0.5,
            "type": "constant",
        },
        "gaussian_wf": {
            "samples": [0.022313984000894595, 0.02301870893368783, 0.023741980663118722, 0.02448415239337985, 0.025245579401142696, 0.026026618874865563, 0.026827629747575098, 0.027648972523077443, 0.028491009095561355, 0.029354102562561588, 0.03023861703125707, 0.031144917418085637, 0.032073369241662965, 0.033024338409001514, 0.03399819099503172, 0.03499529301543567, 0.036016010192810914, 0.03706070771619045, 0.03812974999395229, 0.03922350040016129, 0.04034232101439346, 0.04148657235510257, 0.042656613106597054, 0.04385279983970452, 0.04507548672621055, 0.04632502524716747, 0.047601763895178506, 0.04890604787077224, 0.05023821877299224, 0.051598614284336215, 0.05298756785018939, 0.05440540835290671, 0.055852459780708456, 0.05732904089156428, 0.05883546487225093, 0.06037203899277868, 0.061939064256393075, 0.0635368350453669, 0.06516563876280997, 0.06682575547073258, 0.06851745752461019, 0.07024100920470605, 0.07199666634441962, 0.07378467595593799, 0.07560527585347775, 0.07745869427441475, 0.07934514949860864, 0.0812648494662392, 0.08321799139448006, 0.08520476139334576, 0.08722533408105593, 0.08927987219927043, 0.09136852622855698, 0.09349143400446146, 0.09564872033455936, 0.09784049661687437, 0.1000668604600577, 0.10232789530572876, 0.10462367005338497, 0.1069542386882945, 0.10931963991279237, 0.11171989678140519, 0.11415501634023631, 0.11662498927104675, 0.11912978954047254, 0.12166937405482284, 0.12424368232090653, 0.12685263611333797, 0.12949613914877553, 0.1321740767675477, 0.13488631562312384, 0.13763270337988676, 0.14041306841966547, 0.14322721955748519, 0.14607494576699184, 0.14895601591600616, 0.151870178512661, 0.15481716146257238, 0.1577966718374916, 0.16080839565588248, 0.1638519976758621, 0.16692712120093964, 0.17003338789898062, 0.17317039763481878, 0.1763377283169297, 0.17953493575857307, 0.1827615535538016, 0.1860170929687262, 0.18930104284841642, 0.1926128695398053, 0.19595201683095684, 0.19931790590704201, 0.2027099353233575, 0.20612748099570785, 0.2095698962084588, 0.2130365116405542, 0.2165266354097755, 0.2200395531355059, 0.22357452802024683, 0.22713080095011554, 0.2307075906145385, 0.2343040936453342, 0.2379194847753636, 0.24155291701690568, 0.24520352185989758, 0.24887040949015815, 0.25255266902769424, 0.25624936878516824, 0.25995955654658376, 0.26368225986622607, 0.26741648638787124, 0.27116122418425553, 0.2749154421167759, 0.2786780902153669, 0.28244810007848004, 0.2862243852930639, 0.29000584187442463, 0.29379134872581925, 0.29757976811761266, 0.3013699461858041, 0.3051607134497058, 0.3089508853485331, 0.3127392627966391, 0.31652463275710657, 0.3203057688333823, 0.3240814318786186, 0.3278503706223609, 0.3316113223141977, 0.3353630133839666, 0.33910416011808525, 0.34283346935155606, 0.3465496391751689, 0.3502513596574042, 0.35393731358051944, 0.3576061771902768, 0.3612566209587533, 0.3648873103596508, 0.36849690665550544, 0.3720840676961773, 0.37564744872797906, 0.3791857032127895, 0.38269748365647566, 0.3861814424459327, 0.3896362326940359, 0.39306050909178, 0.39645292876687066, 0.39981215214801763, 0.403136843834164, 0.4064256734678781, 0.4096773166121201, 0.4128904556295857, 0.41606378056382193, 0.41919599002129804, 0.42228579205361055, 0.4253319050389923, 0.42833305856229176, 0.4312879942925826, 0.4341954668575614, 0.43705424471388854, 0.4398631110126247, 0.44262086445891713, 0.44532632016508844, 0.44797831049628406, 0.45057568590783603, 0.4531173157735052, 0.45560208920376954, 0.4580289158533306, 0.4603967267170193, 0.4627044749132883, 0.4649511364544897, 0.46713571100314455, 0.4692572226134244, 0.47131472045707595, 0.4733072795330334, 0.4752340013599784, 0.47709401465112145, 0.4788864759704969, 0.48061057037007826, 0.4822655120070424, 0.48385054474052613, 0.48536494270724323, 0.4868080108753469, 0.4881790855759471, 0.48947753501171326, 0.4907027597420176, 0.4918541931440967, 0.4929313018497351, 0.49393358615700017, 0.49486058041658254, 0.4957118533923249, 0.4964870085955472, 0.497185684592807, 0.49780755528675896, 0.498352330169809, 0.4988197545502864, 0.49920960975088746, 0.4995217132791747, 0.4997559189699447, 0.4999121170993094] + [0.49999023447036683] * 2 + [0.4999121170993094, 0.4997559189699447, 0.4995217132791747, 0.49920960975088746, 0.4988197545502864, 0.498352330169809, 0.49780755528675896, 0.497185684592807, 0.4964870085955472, 0.4957118533923249, 0.49486058041658254, 0.49393358615700017, 0.4929313018497351, 0.4918541931440967, 0.4907027597420176, 0.48947753501171326, 0.4881790855759471, 0.4868080108753469, 0.48536494270724323, 0.48385054474052613, 0.4822655120070424, 0.48061057037007826, 0.4788864759704969, 0.47709401465112145, 0.4752340013599784, 0.4733072795330334, 0.47131472045707595, 0.4692572226134244, 0.46713571100314455, 0.4649511364544897, 0.4627044749132883, 0.4603967267170193, 0.4580289158533306, 0.45560208920376954, 0.4531173157735052, 0.45057568590783603, 0.44797831049628406, 0.44532632016508844, 0.44262086445891713, 0.4398631110126247, 0.43705424471388854, 0.4341954668575614, 0.4312879942925826, 0.42833305856229176, 0.4253319050389923, 0.42228579205361055, 0.41919599002129804, 0.41606378056382193, 0.4128904556295857, 0.4096773166121201, 0.4064256734678781, 0.403136843834164, 0.39981215214801763, 0.39645292876687066, 0.39306050909178, 0.3896362326940359, 0.3861814424459327, 0.38269748365647566, 0.3791857032127895, 0.37564744872797906, 0.3720840676961773, 0.36849690665550544, 0.3648873103596508, 0.3612566209587533, 0.3576061771902768, 0.35393731358051944, 0.3502513596574042, 0.3465496391751689, 0.34283346935155606, 0.33910416011808525, 0.3353630133839666, 0.3316113223141977, 0.3278503706223609, 0.3240814318786186, 0.3203057688333823, 0.31652463275710657, 0.3127392627966391, 0.3089508853485331, 0.3051607134497058, 0.3013699461858041, 0.29757976811761266, 0.29379134872581925, 0.29000584187442463, 0.2862243852930639, 0.28244810007848004, 0.2786780902153669, 0.2749154421167759, 0.27116122418425553, 0.26741648638787124, 0.26368225986622607, 0.25995955654658376, 0.25624936878516824, 0.25255266902769424, 0.24887040949015815, 0.24520352185989758, 0.24155291701690568, 0.2379194847753636, 0.2343040936453342, 0.2307075906145385, 0.22713080095011554, 0.22357452802024683, 0.2200395531355059, 0.2165266354097755, 0.2130365116405542, 0.2095698962084588, 0.20612748099570785, 0.2027099353233575, 0.19931790590704201, 0.19595201683095684, 0.1926128695398053, 0.18930104284841642, 0.1860170929687262, 0.1827615535538016, 0.17953493575857307, 0.1763377283169297, 0.17317039763481878, 0.17003338789898062, 0.16692712120093964, 0.1638519976758621, 0.16080839565588248, 0.1577966718374916, 0.15481716146257238, 0.151870178512661, 0.14895601591600616, 0.14607494576699184, 0.14322721955748519, 0.14041306841966547, 0.13763270337988676, 0.13488631562312384, 0.1321740767675477, 0.12949613914877553, 0.12685263611333797, 0.12424368232090653, 0.12166937405482284, 0.11912978954047254, 0.11662498927104675, 0.11415501634023631, 0.11171989678140519, 0.10931963991279237, 0.1069542386882945, 0.10462367005338497, 0.10232789530572876, 0.1000668604600577, 0.09784049661687437, 0.09564872033455936, 0.09349143400446146, 0.09136852622855698, 0.08927987219927043, 0.08722533408105593, 0.08520476139334576, 0.08321799139448006, 0.0812648494662392, 0.07934514949860864, 0.07745869427441475, 0.07560527585347775, 0.07378467595593799, 0.07199666634441962, 0.07024100920470605, 0.06851745752461019, 0.06682575547073258, 0.06516563876280997, 0.0635368350453669, 0.061939064256393075, 0.06037203899277868, 0.05883546487225093, 0.05732904089156428, 0.055852459780708456, 0.05440540835290671, 0.05298756785018939, 0.051598614284336215, 0.05023821877299224, 0.04890604787077224, 0.047601763895178506, 0.04632502524716747, 0.04507548672621055, 0.04385279983970452, 0.042656613106597054, 0.04148657235510257, 0.04034232101439346, 0.03922350040016129, 0.03812974999395229, 0.03706070771619045, 0.036016010192810914, 0.03499529301543567, 0.03399819099503172, 0.033024338409001514, 0.032073369241662965, 0.031144917418085637, 0.03023861703125707, 0.029354102562561588, 0.028491009095561355, 0.027648972523077443, 0.026827629747575098, 0.026026618874865563, 0.025245579401142696, 0.02448415239337985, 0.023741980663118722, 0.02301870893368783, 0.022313984000894595],
            "type": "arbitrary",
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "pi_wf": {
            "sample": 0.5,
            "type": "constant",
        },
        "pi_half_wf": {
            "sample": 0.25,
            "type": "constant",
        },
        "minus_pi_half_wf": {
            "sample": -0.25,
            "type": "constant",
        },
        "zero_wf": {
            "sample": 0.0,
            "type": "constant",
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [(1, 0)],
        },
        "OFF": {
            "samples": [(0, 0)],
        },
        "spa_trigger": {
            "samples": [(1, 0)],
        },
        "LASER_ON": {
            "samples": [(1, 0)],
        },
    },
    "integration_weights": {
        "cos_weights": {
            "cosine": [(1.0, 4000)],
            "sine": [(0.0, 4000)],
        },
        "sin_weights": {
            "cosine": [(0.0, 4000)],
            "sine": [(1.0, 4000)],
        },
        "minus_sin_weights": {
            "cosine": [(0.0, 4000)],
            "sine": [(-1.0, 4000)],
        },
    },
    "mixers": {
        "mixer_spin1": [{'intermediate_frequency': 100000000.0, 'lo_frequency': 4480887500.0, 'correction': [1.0, 0.0, 0.0, 1.0]}],
        "mixer_spin2": [{'intermediate_frequency': 100000000.0, 'lo_frequency': 4480887500.0, 'correction': [1.0, 0.0, 0.0, 1.0]}],
    },
}


