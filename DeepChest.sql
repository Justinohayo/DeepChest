CREATE TABLE `clinic` (
 `clinicID` varchar(15) NOT NULL,
  `city` varchar(15) NOT NULL,
   `province` varchar(15) NOT NULL,
    `postalCode` varchar(15) NOT NULL,
     primary key (clinicID) 
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO `clinic` (`clinicID`,`city`,`province`,`postalCode`) VALUES
('clinic1','Surrey','BC','V3N0L3');

CREATE TABLE `login` (
  `USERID` varchar(50) NOT NULL,
  `username` varchar(15) NOT NULL,
  `password` varchar(15) NOT NULL,
  `userType` varchar(15) NOT NULL,
  `clinicID` varchar(15) NOT NULL,
    PRIMARY KEY(USERID),
    FOREIGN KEY (clinicID) REFERENCES clinic(clinicID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO `login` ( `USERID`,`username`, `password`, `userType`, `clinicID`) VALUES
('111','treddy','1234', 'patient','clinic1'),
('222','doc1','1234', 'doctor','clinic1'),
('333','admin1','1234', 'clinicadmin','clinic1');

CREATE TABLE `doctor` (
  `firstName` varchar(50) NOT NULL,
  `lastName` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `phone` varchar(15) ,
  `USERID` varchar(50) NOT NULL,
   `clinicID` varchar(15) NOT NULL,
   PRIMARY KEY (USERID),
    FOREIGN KEY (USERID) REFERENCES login(USERID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO `doctor` (`firstName`, `lastName`, `email`, `phone`, `USERID`,`clinicID`) VALUES
('John', 'Doe', 'JohnD@gmail.com',7783123199, '222','clinic1');

CREATE TABLE `patient`(
    `firstName` varchar(50) NOT NULL,
    `lastName` varchar(50) NOT NULL,
    `age` int(2),
    `dateofbirth` date,
    `USERID` varchar(50) NOT NULL UNIQUE,
    `address` varchar(50) NOT NULL,
    `city` varchar(50) NOT NULL,
    `province` varchar(50) NOT NULL,
    `postalCode` varchar(20) NOT NULL,
   `phone` varchar(20),
    `email` varchar(50) NOT NULL UNIQUE,
    `insurance` varchar(20),
    `doctorID` varchar(20),
    `childID`varchar(15) DEFAULT NULL,
     `clinicID` varchar(15) NOT NULL,
    PRIMARY KEY (USERID),
    FOREIGN KEY (USERID) REFERENCES login(USERID),
    FOREIGN KEY (doctorID) REFERENCES doctor(USERID),
    FOREIGN KEY (clinicID) REFERENCES clinic(clinicID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO `patient` (`firstName`, `lastName`, `age`,`dateofbirth`, `USERID`, `address`, `city`, `province`, `postalCode`, `phone`, `email`,`insurance`,`doctorID`,`childID`,`clinicID`) VALUES
('Theisen', 'Reddy', '23','2001-08-25', '111', 'Apt 12 16325 123 St', 'Surrey', 'BC', 'V3N0L3','(604) 545-8690', 'treddy@example.com','Blue Cross','222','','clinic1');


CREATE TABLE `appointments` (
`apptID` int(255) AUTO_INCREMENT,
`patientID` varchar(50) NOT NULL,
`appointment_date` date NOT NULL,
`appointment_time` time NOT NULL,
`doctorID` varchar(20),
`symptoms` varchar(20),
PRIMARY KEY (apptID),
  FOREIGN KEY (patientID) REFERENCES patient(USERID),
   FOREIGN KEY (doctorID) REFERENCES doctor(USERID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;


INSERT INTO `appointments` (`apptID`,`patientID`, `appointment_date`, `appointment_time`, `doctorID`,`symptoms`) VALUES
(1,111,  '2024-03-11', '14:39:00','222','flu like');

CREATE TABLE `Reports` (
  `reportID` varchar(50) NOT NULL,
  `patientID` varchar(255) NOT NULL,
  `doctorID` varchar(255),
  `files` varbinary(255),
   FOREIGN KEY (patientID) REFERENCES patient(USERID),
   FOREIGN KEY (doctorID) REFERENCES doctor(USERID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;


CREATE TABLE `clinicadmin` (
  `USERID` varchar(50) NOT NULL,
 `clinicID` varchar(15) NOT NULL,
    FOREIGN KEY (USERID) REFERENCES login(USERID),
     FOREIGN KEY (clinicID) REFERENCES clinic(clinicID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO `clinicadmin` (`USERID`,`clinicID`) VALUES
('333','clinic1');

CREATE TABLE `childLink` (
  `linkID` int(255) AUTO_INCREMENT,
  `childID` varchar(50) NOT NULL,
 `parentID` varchar(15) NOT NULL,
 PRIMARY KEY (linkID),
    FOREIGN KEY (parentID) REFERENCES patient(USERID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;


CREATE TABLE `child` (
  `childID` varchar(50) NOT NULL,
 `parentID` varchar(15) NOT NULL,
    FOREIGN KEY (parentID) REFERENCES patient(USERID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;


CREATE TABLE `Xrays` (
  `xrayID` varchar(50) NOT NULL,
  `patientID` varchar(255) NOT NULL,
  `doctorID` varchar(255),
  `files` varbinary(255),
     FOREIGN KEY (patientID) REFERENCES patient(USERID),
   FOREIGN KEY (doctorID) REFERENCES doctor(USERID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

CREATE TABLE `messages` (
`messageID` int(255) AUTO_INCREMENT,
`patientID` varchar(50) NOT NULL,
`doctorID` varchar(20),
`content` varchar(20),
`time_sent` timestamp NOT NULL DEFAULT current_timestamp(),
PRIMARY KEY (messageID),
   FOREIGN KEY (patientID) REFERENCES patient(USERID),
   FOREIGN KEY (doctorID) REFERENCES doctor(USERID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;