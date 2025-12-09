"""Mock Data for Verification Services."""

# Valid State Codes (2025 List subset)
STATE_CODES = {
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "29": "Karnataka",
    "27": "Maharashtra",
    "33": "Tamil Nadu",
    "07": "Delhi",
    "09": "Uttar Pradesh",
    "19": "West Bengal",
    "32": "Kerala",
    "08": "Rajasthan",
    "24": "Gujarat",
    "03": "Punjab",
    "06": "Haryana",
}

# 1. GST Portal Mock (Valid Invoices)
# Updated with Valid GSTINs
VALID_GST_INVOICES = {
    "INV-2025-001": {
        "vendor": "Jaipur Gems", 
        "amount": 872660.59, 
        "date": "2025-04-26",
        "gstin": "33VNUIM2761EZX"  # Tamil Nadu
    },
    "INV-2025-002": {
        "vendor": "Warangal Rice", 
        "amount": 308783.01, 
        "date": "2025-03-24",
        "gstin": "37WLZNU4271QZQ"  # Andhra Pradesh
    },
    "INV-2025-003": {
        "vendor": "Chennai Electronics", 
        "amount": 150682.66, 
        "date": "2025-03-27",
        "gstin": "29BFBRJ8715SZE"  # Karnataka
    },
    "INV-2025-004": {
        "vendor": "Bhopal Soy", 
        "amount": 829548.78, 
        "date": "2025-02-18",
        "gstin": "29ZWGYQ9963YZW"  # Karnataka
    },
    "INV-2025-005": {
        "vendor": "Jammu Wool", 
        "amount": 114419.3, 
        "date": "2025-03-26",
        "gstin": "09TYWSI6067KZE"  # Uttar Pradesh
    },
    "INV-2025-006": {
        "vendor": "Hyderabad Spices", 
        "amount": 164539.53, 
        "date": "2025-04-08",
        "gstin": "37KLDPI4744TZK"  # Andhra Pradesh
    },
    "INV-2025-007": {
        "vendor": "Kochi Marine", 
        "amount": 171506.9, 
        "date": "2025-02-25",
        "gstin": "19CBOBA9965YZI"  # West Bengal
    },
    "INV-2025-008": {
        "vendor": "Trichy Engineering", 
        "amount": 845050.6, 
        "date": "2025-02-03",
        "gstin": "36MJUSO4964WZA"  # Telangana
    },
    "INV-2025-009": {
        "vendor": "Madurai Textiles", 
        "amount": 441074.83, 
        "date": "2025-04-21",
        "gstin": "33JZXER6556GZH"  # Tamil Nadu
    },
    "INV-2025-010": {
        "vendor": "Kerala Spices", 
        "amount": 706820.94, 
        "date": "2025-03-14",
        "gstin": "19YWRPX4258TZX"  # West Bengal
    },
    "INV-2025-011": {
        "vendor": "Jaipur Gems", 
        "amount": 580995.43, 
        "date": "2025-01-22",
        "gstin": "08FUJKG8458FZR"  # Rajasthan
    },
    "INV-2025-012": {
        "vendor": "Ahmedabad Chemicals", 
        "amount": 289227.37, 
        "date": "2025-02-09",
        "gstin": "06WPBMZ2893OZH"  # Haryana
    },
    "INV-2025-013": {
        "vendor": "Jaipur Rugs", 
        "amount": 843399.0, 
        "date": "2025-03-16",
        "gstin": "37YOONZ3842AZ2"  # Andhra Pradesh
    },
    "INV-2025-014": {
        "vendor": "Tech Solutions", 
        "amount": 839035.56, 
        "date": "2025-04-28",
        "gstin": "24JDFRU6662UZZ"  # Gujarat
    },
    "INV-2025-015": {
        "vendor": "Indore Cotton", 
        "amount": 561786.9, 
        "date": "2025-03-07",
        "gstin": "07GVMGI8717HZ0"  # Delhi
    },
    "INV-2025-016": {
        "vendor": "Ahmedabad Chemicals", 
        "amount": 572868.97, 
        "date": "2025-03-02",
        "gstin": "07VRTZG1017GZO"  # Delhi
    },
    "INV-2025-017": {
        "vendor": "Tech Solutions", 
        "amount": 737002.09, 
        "date": "2025-04-05",
        "gstin": "27GSWEP0507OZG"  # Maharashtra
    },
    "INV-2025-018": {
        "vendor": "Indore Cotton", 
        "amount": 534974.99, 
        "date": "2025-03-23",
        "gstin": "09DZXGR0715WZ2"  # Uttar Pradesh
    },
    "INV-2025-019": {
        "vendor": "Guwahati Tea", 
        "amount": 430391.84, 
        "date": "2025-03-06",
        "gstin": "19WDIKZ2421XZT"  # West Bengal
    },
    "INV-2025-020": {
        "vendor": "Gurgaon IT", 
        "amount": 374885.9, 
        "date": "2025-04-13",
        "gstin": "08NYMLS0955WZ1"  # Rajasthan
    },
    "INV-2025-021": {
        "vendor": "Kolkata Jute", 
        "amount": 313444.87, 
        "date": "2025-02-28",
        "gstin": "07CTGMT7075RZW"  # Delhi
    },
    "INV-2025-022": {
        "vendor": "Mysore Sandal", 
        "amount": 566221.05, 
        "date": "2025-01-13",
        "gstin": "24YVYVC5965DZU"  # Gujarat
    },
    "INV-2025-023": {
        "vendor": "Bangalore Tech", 
        "amount": 792303.29, 
        "date": "2025-03-05",
        "gstin": "29WCHHI2754CZN"  # Karnataka
    },
    "INV-2025-024": {
        "vendor": "Raipur Coal", 
        "amount": 881835.27, 
        "date": "2025-01-05",
        "gstin": "24FKZMM5349DZB"  # Gujarat
    },
    "INV-2025-025": {
        "vendor": "Goa Cashews", 
        "amount": 371783.3, 
        "date": "2025-04-25",
        "gstin": "32MQWUA4563ZZR"  # Kerala
    },
    "INV-2025-026": {
        "vendor": "Goa Cashews", 
        "amount": 766200.43, 
        "date": "2025-01-26",
        "gstin": "27LEPRG2891IZ3"  # Maharashtra
    },
    "INV-2025-027": {
        "vendor": "Shillong Handicrafts", 
        "amount": 744347.39, 
        "date": "2025-03-22",
        "gstin": "07ERIVT8034CZP"  # Delhi
    },
    "INV-2025-028": {
        "vendor": "Srinagar Carpets", 
        "amount": 408771.86, 
        "date": "2025-01-16",
        "gstin": "33TWTDJ1773XZW"  # Tamil Nadu
    },
    "INV-2025-029": {
        "vendor": "Shimla Apples", 
        "amount": 385183.0, 
        "date": "2025-03-07",
        "gstin": "37VPLHZ2495DZC"  # Andhra Pradesh
    },
    "INV-2025-030": {
        "vendor": "Ahmedabad Chemicals", 
        "amount": 173118.88, 
        "date": "2025-01-27",
        "gstin": "32OWWBP5645NZN"  # Kerala
    },
    "INV-2025-031": {
        "vendor": "Pune Auto", 
        "amount": 15122.49, 
        "date": "2025-01-19",
        "gstin": "37SPJSQ9908UZC"  # Andhra Pradesh
    },
    "INV-2025-032": {
        "vendor": "Madras Cement", 
        "amount": 670001.36, 
        "date": "2025-01-11",
        "gstin": "06XOGTP0914EZE"  # Haryana
    },
    "INV-2025-033": {
        "vendor": "Kolkata Jute", 
        "amount": 16800.91, 
        "date": "2025-03-26",
        "gstin": "33XWPPL5236XZZ"  # Tamil Nadu
    },
    "INV-2025-034": {
        "vendor": "Shillong Handicrafts", 
        "amount": 557919.41, 
        "date": "2025-03-22",
        "gstin": "33TWHQO8150NZY"  # Tamil Nadu
    },
    "INV-2025-035": {
        "vendor": "Tech Solutions", 
        "amount": 683475.21, 
        "date": "2025-01-01",
        "gstin": "32VRKKK8235ZZ3"  # Kerala
    },
    "INV-2025-036": {
        "vendor": "Goa Cashews", 
        "amount": 992286.85, 
        "date": "2025-02-28",
        "gstin": "27VWXBW0755QZ9"  # Maharashtra
    },
    "INV-2025-037": {
        "vendor": "Coimbatore Mills", 
        "amount": 906190.2, 
        "date": "2025-01-19",
        "gstin": "03XESBC2133PZM"  # Punjab
    },
    "INV-2025-038": {
        "vendor": "Vizag Steel", 
        "amount": 961780.78, 
        "date": "2025-03-02",
        "gstin": "07CYSKJ7416BZA"  # Delhi
    },
    "INV-2025-039": {
        "vendor": "Bhubaneswar Iron", 
        "amount": 47775.68, 
        "date": "2025-04-06",
        "gstin": "24MBCOW9034HZB"  # Gujarat
    },
    "INV-2025-040": {
        "vendor": "Hyderabad Spices", 
        "amount": 26960.57, 
        "date": "2025-04-21",
        "gstin": "24OXVQU9159PZW"  # Gujarat
    },
    "INV-2025-041": {
        "vendor": "Haridwar Pharma", 
        "amount": 578389.02, 
        "date": "2025-04-15",
        "gstin": "29WDOWS3319VZS"  # Karnataka
    },
    "INV-2025-042": {
        "vendor": "Lucknow Leather", 
        "amount": 372579.67, 
        "date": "2025-01-15",
        "gstin": "09NUBES6614YZ5"  # Uttar Pradesh
    },
    "INV-2025-043": {
        "vendor": "Coimbatore Mills", 
        "amount": 992511.46, 
        "date": "2025-03-10",
        "gstin": "32RHSDK6861NZV"  # Kerala
    },
    "INV-2025-044": {
        "vendor": "Mysore Sandal", 
        "amount": 747827.37, 
        "date": "2025-02-27",
        "gstin": "29AOGIU6208DZE"  # Karnataka
    },
    "INV-2025-045": {
        "vendor": "Madras Cement", 
        "amount": 161803.87, 
        "date": "2025-01-13",
        "gstin": "08VYXLL3396XZP"  # Rajasthan
    },
    "INV-2025-046": {
        "vendor": "Raipur Coal", 
        "amount": 60816.82, 
        "date": "2025-01-23",
        "gstin": "03VBWDF9168TZ2"  # Punjab
    },
    "INV-2025-047": {
        "vendor": "Madurai Textiles", 
        "amount": 166819.03, 
        "date": "2025-01-12",
        "gstin": "08BBIGO4900YZC"  # Rajasthan
    },
    "INV-2025-048": {
        "vendor": "Dehradun Rice", 
        "amount": 709035.81, 
        "date": "2025-04-05",
        "gstin": "37YJGVV1847ZZX"  # Andhra Pradesh
    },
    "INV-2025-049": {
        "vendor": "Tech Solutions", 
        "amount": 134773.15, 
        "date": "2025-01-21",
        "gstin": "07BMJMO3108TZC"  # Delhi
    },
    "INV-2025-050": {
        "vendor": "Kisan World", 
        "amount": 803025.97, 
        "date": "2025-03-05",
        "gstin": "36OHGEJ5401AZF"  # Telangana
    },
    "INV-2025-051": {
        "vendor": "Kisan World", 
        "amount": 745998.28, 
        "date": "2025-02-17",
        "gstin": "36BTNDK2481YZ7"  # Telangana
    },
    "INV-2025-052": {
        "vendor": "Mysore Sandal", 
        "amount": 843328.4, 
        "date": "2025-01-14",
        "gstin": "27NSWDT9703UZG"  # Maharashtra
    },
    "INV-2025-053": {
        "vendor": "Shimla Apples", 
        "amount": 538065.28, 
        "date": "2025-03-05",
        "gstin": "06JBUAW3462YZC"  # Haryana
    },
    "INV-2025-054": {
        "vendor": "Shimla Apples", 
        "amount": 847891.08, 
        "date": "2025-02-15",
        "gstin": "37BIUZM0418XZW"  # Andhra Pradesh
    },
    "INV-2025-055": {
        "vendor": "Kerala Spices", 
        "amount": 292480.26, 
        "date": "2025-01-28",
        "gstin": "32KLRHK3785JZ3"  # Kerala
    },
    "INV-2025-056": {
        "vendor": "Vizag Steel", 
        "amount": 397867.23, 
        "date": "2025-02-11",
        "gstin": "24XSJWO2697MZI"  # Gujarat
    },
    "INV-2025-057": {
        "vendor": "Agri Supplies", 
        "amount": 41711.1, 
        "date": "2025-02-01",
        "gstin": "07RVNGS7311LZN"  # Delhi
    },
    "INV-2025-058": {
        "vendor": "Goa Cashews", 
        "amount": 504365.26, 
        "date": "2025-01-13",
        "gstin": "07MFECE3134AZQ"  # Delhi
    },
    "INV-2025-059": {
        "vendor": "Ranchi Steel", 
        "amount": 652466.03, 
        "date": "2025-01-15",
        "gstin": "07CWNFC9087PZS"  # Delhi
    },
    "INV-2025-060": {
        "vendor": "Guwahati Tea", 
        "amount": 606271.99, 
        "date": "2025-02-04",
        "gstin": "06SFENZ6115NZM"  # Haryana
    },
    "INV-2025-061": {
        "vendor": "Jammu Wool", 
        "amount": 357963.67, 
        "date": "2025-01-08",
        "gstin": "08YYWJX4262SZW"  # Rajasthan
    },
    "INV-2025-062": {
        "vendor": "Belgaum Foundry", 
        "amount": 227995.8, 
        "date": "2025-03-13",
        "gstin": "37FFBTF8626MZ3"  # Andhra Pradesh
    },
    "INV-2025-063": {
        "vendor": "Warangal Rice", 
        "amount": 102446.83, 
        "date": "2025-04-14",
        "gstin": "37NLPIB9798AZ8"  # Andhra Pradesh
    },
    "INV-2025-064": {
        "vendor": "Shimla Apples", 
        "amount": 731314.83, 
        "date": "2025-04-04",
        "gstin": "32JOHNF8090TZD"  # Kerala
    },
    "INV-2025-065": {
        "vendor": "Lucknow Leather", 
        "amount": 404407.34, 
        "date": "2025-01-14",
        "gstin": "24RUXUY8650GZB"  # Gujarat
    },
    "INV-2025-066": {
        "vendor": "Nagpur Oranges", 
        "amount": 625296.76, 
        "date": "2025-03-24",
        "gstin": "07PWSVP4315TZ3"  # Delhi
    },
    "INV-2025-067": {
        "vendor": "Kisan World", 
        "amount": 170680.84, 
        "date": "2025-03-06",
        "gstin": "07EZJRF3650FZM"  # Delhi
    },
    "INV-2025-068": {
        "vendor": "Kisan World", 
        "amount": 992096.18, 
        "date": "2025-01-09",
        "gstin": "32UTSFL3815DZE"  # Kerala
    },
    "INV-2025-069": {
        "vendor": "Lucknow Leather", 
        "amount": 795015.63, 
        "date": "2025-04-03",
        "gstin": "08RHTWY8202MZM"  # Rajasthan
    },
    "INV-2025-070": {
        "vendor": "Jaipur Rugs", 
        "amount": 335488.15, 
        "date": "2025-03-14",
        "gstin": "03MVBIS8746SZI"  # Punjab
    },
    "INV-2025-071": {
        "vendor": "Bangalore Tech", 
        "amount": 687045.25, 
        "date": "2025-03-17",
        "gstin": "19EOWTD4496XZ1"  # West Bengal
    },
    "INV-2025-072": {
        "vendor": "Dehradun Rice", 
        "amount": 147664.36, 
        "date": "2025-03-02",
        "gstin": "06IFXRP1157OZE"  # Haryana
    },
    "INV-2025-073": {
        "vendor": "Madras Cement", 
        "amount": 564398.46, 
        "date": "2025-03-14",
        "gstin": "33ZZEKK5007YZL"  # Tamil Nadu
    },
    "INV-2025-074": {
        "vendor": "Mysore Sandal", 
        "amount": 489778.4, 
        "date": "2025-03-02",
        "gstin": "32QNVTU1352MZP"  # Kerala
    },
    "INV-2025-075": {
        "vendor": "Bhopal Soy", 
        "amount": 410169.42, 
        "date": "2025-03-27",
        "gstin": "09WKVWV4376AZ8"  # Uttar Pradesh
    },
    "INV-2025-076": {
        "vendor": "Noida Mobiles", 
        "amount": 932110.62, 
        "date": "2025-04-07",
        "gstin": "24XKLYD5126TZ5"  # Gujarat
    },
    "INV-2025-077": {
        "vendor": "Jaipur Rugs", 
        "amount": 319572.44, 
        "date": "2025-04-21",
        "gstin": "27XTYEY2888AZU"  # Maharashtra
    },
    "INV-2025-078": {
        "vendor": "Kisan World", 
        "amount": 239270.44, 
        "date": "2025-02-14",
        "gstin": "32BGYPO1118BZC"  # Kerala
    },
    "INV-2025-079": {
        "vendor": "Mysore Sandal", 
        "amount": 979556.56, 
        "date": "2025-04-03",
        "gstin": "06JHFVX6343IZ6"  # Haryana
    },
    "INV-2025-080": {
        "vendor": "Hubli Cotton", 
        "amount": 198725.85, 
        "date": "2025-03-11",
        "gstin": "32FGKMW8424ZZI"  # Kerala
    },
    "INV-2025-081": {
        "vendor": "Madurai Textiles", 
        "amount": 303158.82, 
        "date": "2025-04-02",
        "gstin": "27DCMWF5609NZV"  # Maharashtra
    },
    "INV-2025-082": {
        "vendor": "Mumbai Traders", 
        "amount": 377342.22, 
        "date": "2025-01-28",
        "gstin": "37GKRDN9829UZB"  # Andhra Pradesh
    },
    "INV-2025-083": {
        "vendor": "Vijayawada Auto", 
        "amount": 345696.09, 
        "date": "2025-04-02",
        "gstin": "03EPQHG0651AZI"  # Punjab
    },
    "INV-2025-084": {
        "vendor": "Bhubaneswar Iron", 
        "amount": 887011.92, 
        "date": "2025-02-24",
        "gstin": "06AJCZJ6254QZA"  # Haryana
    },
    "INV-2025-085": {
        "vendor": "Jaipur Gems", 
        "amount": 859106.3, 
        "date": "2025-04-08",
        "gstin": "24JUZHM1868QZS"  # Gujarat
    },
    "INV-2025-086": {
        "vendor": "Hubli Cotton", 
        "amount": 497443.27, 
        "date": "2025-03-22",
        "gstin": "24VTSJA0357LZS"  # Gujarat
    },
    "INV-2025-087": {
        "vendor": "Belgaum Foundry", 
        "amount": 329507.45, 
        "date": "2025-02-21",
        "gstin": "09ZVGJS6172UZ2"  # Uttar Pradesh
    },
    "INV-2025-088": {
        "vendor": "Vizag Steel", 
        "amount": 521948.71, 
        "date": "2025-01-17",
        "gstin": "08WDJRP8103KZM"  # Rajasthan
    },
    "INV-2025-089": {
        "vendor": "Nagpur Oranges", 
        "amount": 812668.22, 
        "date": "2025-02-09",
        "gstin": "07JLCJF1251UZP"  # Delhi
    },
    "INV-2025-090": {
        "vendor": "Bhopal Soy", 
        "amount": 833599.79, 
        "date": "2025-01-17",
        "gstin": "09QURYD7727VZX"  # Uttar Pradesh
    },
    "INV-2025-091": {
        "vendor": "Srinagar Carpets", 
        "amount": 27521.05, 
        "date": "2025-01-11",
        "gstin": "37XNFAR9471OZQ"  # Andhra Pradesh
    },
    "INV-2025-092": {
        "vendor": "Surat Textiles", 
        "amount": 112884.5, 
        "date": "2025-01-05",
        "gstin": "24JDAUH8022LZZ"  # Gujarat
    },
    "INV-2025-093": {
        "vendor": "Madurai Textiles", 
        "amount": 115955.07, 
        "date": "2025-02-26",
        "gstin": "07UNBFB0423CZV"  # Delhi
    },
    "INV-2025-094": {
        "vendor": "Agri Supplies", 
        "amount": 474170.07, 
        "date": "2025-01-15",
        "gstin": "07TGPFA5052YZH"  # Delhi
    },
    "INV-2025-095": {
        "vendor": "Gurgaon IT", 
        "amount": 908029.81, 
        "date": "2025-03-19",
        "gstin": "09QTFWT3602ZZ1"  # Uttar Pradesh
    },
    "INV-2025-096": {
        "vendor": "Madurai Textiles", 
        "amount": 654955.55, 
        "date": "2025-01-04",
        "gstin": "08LWUGS8699NZZ"  # Rajasthan
    },
    "INV-2025-097": {
        "vendor": "Belgaum Foundry", 
        "amount": 112228.13, 
        "date": "2025-03-07",
        "gstin": "33FBAVA3420KZU"  # Tamil Nadu
    },
    "INV-2025-098": {
        "vendor": "Tirupati Laddu", 
        "amount": 332772.77, 
        "date": "2025-01-05",
        "gstin": "33ZTQAQ0884TZ7"  # Tamil Nadu
    },
    "INV-2025-099": {
        "vendor": "Nagpur Oranges", 
        "amount": 533375.46, 
        "date": "2025-03-21",
        "gstin": "03UCEGA3547QZ2"  # Punjab
    },
    "INV-2025-100": {
        "vendor": "Jaipur Gems", 
        "amount": 583685.69, 
        "date": "2025-01-24",
        "gstin": "09OVVVE6643VZ9"  # Uttar Pradesh
    },
    "GST-999-XYZ": {
        "vendor": "Fake Vendor", 
        "amount": 12000.0, 
        "date": "2025-02-01",
        "gstin": "99ZZZZZ9999Z1Z1"  # Invalid State 99
    }
}

# 2. Bank Core System Mock (Sanctioned Loans)
# Maps Applicant ID -> Asset Type they are allowed to buy
SANCTIONED_LOANS = {
    "APPLICANT-123": {"allowed_asset": "rice transplanter", "max_amount": 153688.43},
    "APPLICANT-456": {"allowed_asset": "tractor", "max_amount": 3133639.63},
    "APPLICANT-789": {"allowed_asset": "borewell pump", "max_amount": 2884658.81},
    "APPLICANT-101": {"allowed_asset": "rice transplanter", "max_amount": 588122.15},
    "APPLICANT-102": {"allowed_asset": "rice transplanter", "max_amount": 4603089.13},
    "APPLICANT-103": {"allowed_asset": "cultivator", "max_amount": 3769165.94},
    "APPLICANT-104": {"allowed_asset": "sugarcane planter", "max_amount": 2234359.49},
    "APPLICANT-105": {"allowed_asset": "cultivator", "max_amount": 3285414.53},
    "APPLICANT-106": {"allowed_asset": "milking machine", "max_amount": 2416894.91},
    "APPLICANT-107": {"allowed_asset": "tractor", "max_amount": 1481006.1},
    "APPLICANT-108": {"allowed_asset": "pumpset", "max_amount": 4527769.23},
    "APPLICANT-109": {"allowed_asset": "power tiller", "max_amount": 4592760.95},
    "APPLICANT-110": {"allowed_asset": "mist blower", "max_amount": 3260394.6},
    "APPLICANT-111": {"allowed_asset": "solar pump", "max_amount": 3678586.02},
    "APPLICANT-112": {"allowed_asset": "thresher", "max_amount": 385529.1},
    "APPLICANT-113": {"allowed_asset": "greenhouse", "max_amount": 2514042.31},
    "APPLICANT-114": {"allowed_asset": "milking machine", "max_amount": 4441546.1},
    "APPLICANT-115": {"allowed_asset": "solar pump", "max_amount": 2166947.28},
    "APPLICANT-116": {"allowed_asset": "milking machine", "max_amount": 2221342.86},
    "APPLICANT-117": {"allowed_asset": "greenhouse", "max_amount": 727351.65},
    "APPLICANT-118": {"allowed_asset": "groundnut digger", "max_amount": 3281949.43},
    "APPLICANT-119": {"allowed_asset": "rotavator", "max_amount": 146111.89},
    "APPLICANT-120": {"allowed_asset": "chaff cutter", "max_amount": 3817154.84},
    "APPLICANT-121": {"allowed_asset": "winnower", "max_amount": 3462853.0},
    "APPLICANT-122": {"allowed_asset": "borewell pump", "max_amount": 4646901.96},
    "APPLICANT-123": {"allowed_asset": "milking machine", "max_amount": 3990251.87},
    "APPLICANT-124": {"allowed_asset": "dryer", "max_amount": 4918388.95},
    "APPLICANT-125": {"allowed_asset": "mini tractor", "max_amount": 4526402.27},
    "APPLICANT-126": {"allowed_asset": "maize sheller", "max_amount": 1516042.33},
    "APPLICANT-127": {"allowed_asset": "groundnut digger", "max_amount": 3002623.13},
    "APPLICANT-128": {"allowed_asset": "storage bin", "max_amount": 569794.57},
    "APPLICANT-129": {"allowed_asset": "combine harvester", "max_amount": 206931.42},
    "APPLICANT-130": {"allowed_asset": "chaff cutter", "max_amount": 2585711.82},
    "APPLICANT-131": {"allowed_asset": "tractor", "max_amount": 4316897.19},
    "APPLICANT-132": {"allowed_asset": "mist blower", "max_amount": 760344.53},
    "APPLICANT-133": {"allowed_asset": "laser leveler", "max_amount": 1321598.56},
    "APPLICANT-134": {"allowed_asset": "harvester", "max_amount": 417923.01},
    "APPLICANT-135": {"allowed_asset": "chaff cutter", "max_amount": 4517677.24},
    "APPLICANT-136": {"allowed_asset": "power weeder", "max_amount": 2930405.85},
    "APPLICANT-137": {"allowed_asset": "mist blower", "max_amount": 694486.64},
    "APPLICANT-138": {"allowed_asset": "power tiller", "max_amount": 225919.39},
    "APPLICANT-139": {"allowed_asset": "crop reaper", "max_amount": 3278987.41},
    "APPLICANT-140": {"allowed_asset": "fodder harvester", "max_amount": 1265943.23},
    "APPLICANT-141": {"allowed_asset": "winnower", "max_amount": 3411908.29},
    "APPLICANT-142": {"allowed_asset": "maize sheller", "max_amount": 4966216.06},
    "APPLICANT-143": {"allowed_asset": "maize sheller", "max_amount": 1885857.97},
    "APPLICANT-144": {"allowed_asset": "tractor", "max_amount": 2496006.42},
    "APPLICANT-145": {"allowed_asset": "combine harvester", "max_amount": 4631511.84},
    "APPLICANT-146": {"allowed_asset": "mulcher", "max_amount": 2207777.64},
    "APPLICANT-147": {"allowed_asset": "drone sprayer", "max_amount": 865399.58},
    "APPLICANT-148": {"allowed_asset": "seed drill", "max_amount": 958773.35},
    "APPLICANT-149": {"allowed_asset": "maize sheller", "max_amount": 2304856.87},
    "APPLICANT-150": {"allowed_asset": "tractor", "max_amount": 4381927.61},
    "APPLICANT-151": {"allowed_asset": "cultivator", "max_amount": 250097.65},
    "APPLICANT-152": {"allowed_asset": "wheel loader", "max_amount": 3218603.93},
    "APPLICANT-153": {"allowed_asset": "laser leveler", "max_amount": 3216312.48},
    "APPLICANT-154": {"allowed_asset": "borewell pump", "max_amount": 4932098.78},
    "APPLICANT-155": {"allowed_asset": "power tiller", "max_amount": 1051630.49},
    "APPLICANT-156": {"allowed_asset": "cultivator", "max_amount": 3459801.61},
    "APPLICANT-157": {"allowed_asset": "milking machine", "max_amount": 2170384.38},
    "APPLICANT-158": {"allowed_asset": "solar pump", "max_amount": 2493021.49},
    "APPLICANT-159": {"allowed_asset": "harrow", "max_amount": 2642250.2},
    "APPLICANT-160": {"allowed_asset": "groundnut digger", "max_amount": 2695987.45},
    "APPLICANT-161": {"allowed_asset": "groundnut digger", "max_amount": 4755411.13},
    "APPLICANT-162": {"allowed_asset": "decorticator", "max_amount": 3859448.15},
    "APPLICANT-163": {"allowed_asset": "baler", "max_amount": 3017344.66},
    "APPLICANT-164": {"allowed_asset": "cotton picker", "max_amount": 113422.82},
    "APPLICANT-165": {"allowed_asset": "mulcher", "max_amount": 4077489.2},
    "APPLICANT-166": {"allowed_asset": "thresher", "max_amount": 2459367.29},
    "APPLICANT-167": {"allowed_asset": "harvester", "max_amount": 4304909.29},
    "APPLICANT-168": {"allowed_asset": "chaff cutter", "max_amount": 2740151.97},
    "APPLICANT-169": {"allowed_asset": "cotton picker", "max_amount": 3725693.89},
    "APPLICANT-170": {"allowed_asset": "chaff cutter", "max_amount": 978154.97},
    "APPLICANT-171": {"allowed_asset": "sugarcane planter", "max_amount": 4283815.16},
    "APPLICANT-172": {"allowed_asset": "mini tractor", "max_amount": 58006.29},
    "APPLICANT-173": {"allowed_asset": "wheel loader", "max_amount": 615919.47},
    "APPLICANT-174": {"allowed_asset": "winnower", "max_amount": 3514677.38},
    "APPLICANT-175": {"allowed_asset": "tractor", "max_amount": 4540161.15},
    "APPLICANT-176": {"allowed_asset": "solar pump", "max_amount": 4855312.09},
    "APPLICANT-177": {"allowed_asset": "baler", "max_amount": 4062945.29},
    "APPLICANT-178": {"allowed_asset": "harrow", "max_amount": 4046736.81},
    "APPLICANT-179": {"allowed_asset": "seed drill", "max_amount": 4115731.42},
    "APPLICANT-180": {"allowed_asset": "pumpset", "max_amount": 3418133.55},
    "APPLICANT-181": {"allowed_asset": "mini tractor", "max_amount": 2596256.04},
    "APPLICANT-182": {"allowed_asset": "groundnut digger", "max_amount": 3831592.11},
    "APPLICANT-183": {"allowed_asset": "borewell pump", "max_amount": 2033416.97},
    "APPLICANT-184": {"allowed_asset": "seed drill", "max_amount": 544989.81},
    "APPLICANT-185": {"allowed_asset": "pumpset", "max_amount": 4818638.31},
    "APPLICANT-186": {"allowed_asset": "power tiller", "max_amount": 3467943.56},
    "APPLICANT-187": {"allowed_asset": "wheel loader", "max_amount": 2014132.48},
    "APPLICANT-188": {"allowed_asset": "plough", "max_amount": 2051404.25},
    "APPLICANT-189": {"allowed_asset": "cultivator", "max_amount": 2210878.94},
    "APPLICANT-190": {"allowed_asset": "tractor", "max_amount": 3509791.56},
    "APPLICANT-191": {"allowed_asset": "laser leveler", "max_amount": 207651.51},
    "APPLICANT-192": {"allowed_asset": "cultivator", "max_amount": 3843658.92},
    "APPLICANT-193": {"allowed_asset": "tractor", "max_amount": 4187871.11},
    "APPLICANT-194": {"allowed_asset": "power weeder", "max_amount": 3197681.48},
    "APPLICANT-195": {"allowed_asset": "rice transplanter", "max_amount": 4608675.26},
    "APPLICANT-196": {"allowed_asset": "harvester", "max_amount": 4853307.49},
    "APPLICANT-197": {"allowed_asset": "pumpset", "max_amount": 1827823.59},
}