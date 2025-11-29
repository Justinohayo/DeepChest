/*
        Creates a Table for clinic that includes clinicID, city, province, and postalCode
        */
CREATE TABLE `clinic` (
 `clinicID` int(255) AUTO_INCREMENT NOT NUll UNIQUE,
 `address` varchar(15) NOT NULL,
  `city` varchar(15) NOT NULL,
   `province` varchar(15) NOT NULL,
    `postalCode` varchar(15) NOT NULL,
     primary key (clinicID) 
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

 -- adds data into the clinic table
INSERT INTO `clinic` (`clinicID`,`address`,`city`,`province`,`postalCode`) VALUES
('1000','12345 82 Ave','Surrey','BC','V3N0L3'),
('2000','1354 162 ST','Vancouver','BC','V5K0A1');
/*
        Creates a Table for login that includes USERID, username, password, userType, and clinicID
        */
CREATE TABLE `login` (
  `USERID`  int(255) AUTO_INCREMENT UNIQUE,
  `username` varchar(50) NOT NULL,
  `password` varchar(15) NOT NULL,
  `userType` varchar(15) NOT NULL,
  `clinicID` int(255) NOT NULL,
    PRIMARY KEY(USERID),
    FOREIGN KEY (clinicID) REFERENCES clinic(clinicID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

 -- adds rows of data to the login table for each user type
INSERT INTO `login` ( `USERID`,`username`, `password`, `userType`, `clinicID`) VALUES
('111','treddy','1234', 'patient','1000'),
('112','example','1234', 'patient','1000'),
('222','doc1','1234', 'doctor','1000'),
('333','admin1','1234', 'clinicadmin','1000');

/*
        Creates a Table for doctors that includes firstName, lastName, email, phone, USERID, and clinicID
        */
CREATE TABLE `doctor` (
  `firstName` varchar(50) NOT NULL,
  `lastName` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `phone` varchar(15) ,
  `USERID` int(255) NOT NULL,
   `clinicID` int(255) NOT NULL,
   PRIMARY KEY (USERID),
    FOREIGN KEY (USERID) REFERENCES login(USERID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

 -- adds data to the doctor table
INSERT INTO `doctor` (`firstName`, `lastName`, `email`, `phone`, `USERID`,`clinicID`) VALUES
('John', 'Doe', 'JohnD@gmail.com',7783123199, '222','1000');
/*
        Creates a Table for patients that includes firstName, lastName, age, dateofbirth, USERID, address, city, province, postalCode, phone, email, insurance, doctorID, childID and clinicID
        */
CREATE TABLE `patient`(
    `firstName` varchar(50) NOT NULL,
    `lastName` varchar(50) NOT NULL,
    `age` int(2),
    `dateofbirth` date,
    `USERID`int(255) ,
    `address` varchar(50) NOT NULL,
    `city` varchar(50) NOT NULL,
    `province` varchar(50) NOT NULL,
    `postalCode` varchar(20) NOT NULL,
   `phone` varchar(20),
    `email` varchar(50) NOT NULL UNIQUE,
    `insurance` varchar(20),
    `doctorID`int(255),
    `childID`varchar(15) DEFAULT NULL,
     `clinicID` int(255) NOT NULL,
    PRIMARY KEY (USERID),
    FOREIGN KEY (USERID) REFERENCES login(USERID),
    FOREIGN KEY (doctorID) REFERENCES doctor(USERID),
    FOREIGN KEY (clinicID) REFERENCES clinic(clinicID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

 -- adds data to the patient table
INSERT INTO `patient` (`firstName`, `lastName`, `age`,`dateofbirth`, `USERID`, `address`, `city`, `province`, `postalCode`, `phone`, `email`,`insurance`,`doctorID`,`childID`,`clinicID`) VALUES
('Theisen', 'Reddy', '23','2001-08-25', '111', 'Apt 12 16325 123 St', 'Surrey', 'BC', 'V3N0L3','(604) 545-8690', 'treddy@example.com','Blue Cross','222','','1000'),
('Example', 'Person', '23','2001-08-25', '112', 'Apt 12 16325 123 St', 'Surrey', 'BC', 'V3N0L3','(604) 545-8690', 'example@example.com','Blue Cross','222','','1000');

/*
        Creates a Table for appointments that includes apptID, patientID, appointment_date, appointment_time, doctorID, and symptoms
        */
CREATE TABLE `appointments` (
`apptID` int(255) AUTO_INCREMENT UNIQUE,
`patientID` int(255) NOT NULL,
`appointment_date` date NOT NULL,
`appointment_time` time NOT NULL,
`doctorID` int(255),
`clinicID` int(255),
`symptoms` varchar(20),
PRIMARY KEY (apptID),
  FOREIGN KEY (patientID) REFERENCES patient(USERID),
   FOREIGN KEY (doctorID) REFERENCES doctor(USERID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

 -- adds data to the appointments table
INSERT INTO `appointments` (`apptID`,`patientID`, `appointment_date`, `appointment_time`, `doctorID`,`clinicID`,`symptoms`) VALUES
(1,111,  '2024-03-11', '14:39:00','222','1000','flu like'),
(2,112,  '2024-03-12', '10:00:00','222','1000','coughing');

/*
        Creates a Table for reports that includes reportID, patientID, doctorID, and files
        */
CREATE TABLE `Reports` (
  `reportID` int(255) AUTO_INCREMENT NOT NULL UNIQUE,
  `patientID` int(255) NOT NULL,
  `doctorID` int(255),
  `reportDate` date NOT NULL,
  `expiryDate` date NOT NULL,
  `files` varbinary(255),
  PRIMARY KEY (reportID),
   FOREIGN KEY (patientID) REFERENCES patient(USERID),
   FOREIGN KEY (doctorID) REFERENCES doctor(USERID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

 -- adds data to the reports table
INSERT INTO `Reports` (`patientID`, `doctorID`, `reportDate`,`expiryDate`, `files`) VALUES
(111, 222, '2025-11-11','2025-12-11' ,'report1.pdf'),
(112, 222, '2025-11-12','2025-12-11' ,'report2.pdf'),
(111, 222, '2025-11-14','2025-12-11', 'report3.pdf');

/*
        Creates a Table for clinic admins that includes USERID and clinicID
        */
CREATE TABLE `clinicadmin` (
  `USERID` int(255) NOT NULL,
 `clinicID` int(255) NOT NULL,
    FOREIGN KEY (USERID) REFERENCES login(USERID),
     FOREIGN KEY (clinicID) REFERENCES clinic(clinicID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

 -- adds data to the clinicadmin table
INSERT INTO `clinicadmin` (`USERID`,`clinicID`) VALUES
('333','1000');

/*
        Creates a Table for child links that includes linkID, childID, and parentID
        */
CREATE TABLE `childLink` (
  `linkID` int(255) AUTO_INCREMENT UNIQUE,
 `parentID` int(255) NOT NULL,
 PRIMARY KEY (linkID),
    FOREIGN KEY (parentID) REFERENCES patient(USERID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*
        Creates a Table for child that includes childID and parentID
        */
CREATE TABLE `child` (
  `childID` int(50) AUTO_INCREMENT NOT NULL UNIQUE,
 `linkID` int(255) NOT NULL,
 `parentID` int(255) NOT NULL,
	PRIMARY KEY (childID),
    FOREIGN KEY (parentID) REFERENCES patient(USERID),
	FOREIGN KEY (linkID) REFERENCES childlink(linkID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*
        Creates a Table for xrays that includes xrayID, patientID, doctorID, and files
        */
/*Add pointers for S3 in this table, drop it before editing*/
CREATE TABLE `Xrays` (
  `xrayID`int(255) AUTO_INCREMENT UNIQUE,
  `patientID` int(255) NOT NULL,
  `doctorID` int(255),
  `date` date NOT NULL,
  `files` varbinary(255),
  PRIMARY KEY (xrayID),
     FOREIGN KEY (patientID) REFERENCES patient(USERID),
   FOREIGN KEY (doctorID) REFERENCES doctor(USERID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

 -- adds data to the xrays table
INSERT INTO `Xrays` (`patientID`, `doctorID`, `date`, `files`) VALUES
(111, 222, '2024-04-11', 'xray1.jpg'),
(112, 222, '2024-04-12', 'xray2.jpg');
/*
        Creates a Table for messages that includes messageID, patientID, doctorID, content, and time_sent
        */
CREATE TABLE `messages` (
`messageID` int(255) AUTO_INCREMENT UNIQUE,
`patientID` int(255) NOT NULL,
`doctorID` int(255),
`content` varchar(255),
`time_sent` timestamp NOT NULL DEFAULT current_timestamp(),
PRIMARY KEY (messageID),
   FOREIGN KEY (patientID) REFERENCES patient(USERID),
   FOREIGN KEY (doctorID) REFERENCES doctor(USERID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

CREATE TABLE `account_update_requests` (
    `requestID` INT AUTO_INCREMENT PRIMARY KEY,
    `doctorID` INT NOT NULL,
    `requested_firstName` VARCHAR(100),
    `requested_lastName` VARCHAR(100),
    `requested_email` VARCHAR(255),
    `requested_phone` VARCHAR(20),
    `request_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (`doctorID`) REFERENCES `doctor`(`USERID`)
);

CREATE TABLE `notifications` (
    `patientID` INT,
    `contact_info` VARCHAR(100),
    `notification_status` BOOLEAN NOT NULL,
    FOREIGN KEY (`patientID`) REFERENCES `patient`(`USERID`)
);