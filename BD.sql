-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: sistema_vision
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `registro_piezas`
--

DROP TABLE IF EXISTS `registro_piezas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registro_piezas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ancho` float NOT NULL,
  `largo` float NOT NULL,
  `valido` tinyint(1) NOT NULL,
  `fecha` datetime NOT NULL,
  `lote` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registro_piezas`
--

LOCK TABLES `registro_piezas` WRITE;
/*!40000 ALTER TABLE `registro_piezas` DISABLE KEYS */;
INSERT INTO `registro_piezas` VALUES (1,4.5,6.2,1,'2025-04-19 10:00:01','LoteA01'),(2,4.3,6.1,1,'2025-04-19 10:00:03','LoteA01'),(3,4.7,6,0,'2025-04-19 10:00:06','LoteA01'),(4,4.6,6.3,1,'2025-04-19 10:00:08','LoteA01'),(5,4.2,6,0,'2025-04-19 10:00:10','LoteA01'),(6,4.4,6.1,1,'2025-04-19 10:00:13','LoteA01'),(7,4.9,6.5,1,'2025-04-19 10:00:15','LoteA01'),(8,4.1,5.9,0,'2025-04-19 10:00:18','LoteA01'),(9,4.6,6.2,1,'2025-04-19 10:00:20','LoteA01'),(10,4.3,6,1,'2025-04-19 10:00:23','LoteA01'),(11,5,6.8,1,'2025-04-19 11:00:01','LoteB02'),(12,4.8,6.6,1,'2025-04-19 11:00:04','LoteB02'),(13,4.7,6.4,0,'2025-04-19 11:00:07','LoteB02'),(14,5.1,6.9,1,'2025-04-19 11:00:09','LoteB02'),(15,4.6,6.5,0,'2025-04-19 11:00:11','LoteB02'),(16,4.9,6.7,1,'2025-04-19 11:00:14','LoteB02'),(17,5.2,7,1,'2025-04-19 11:00:17','LoteB02'),(18,4.5,6.3,0,'2025-04-19 11:00:20','LoteB02'),(19,5,6.8,1,'2025-04-19 11:00:22','LoteB02'),(20,4.8,6.6,1,'2025-04-19 11:00:25','LoteB02'),(21,5,6.8,0,'2025-04-19 11:00:01','LoteC03'),(22,4.8,6.6,0,'2025-04-19 11:00:04','LoteC03'),(23,4.7,6.4,0,'2025-04-19 11:00:07','LoteC03'),(24,5.1,6.9,1,'2025-04-19 11:00:09','LoteC03'),(25,4.6,6.5,0,'2025-04-19 11:00:11','LoteC03'),(26,4.9,6.7,1,'2025-04-19 11:00:14','LoteC03'),(27,5.2,7,0,'2025-04-19 11:00:17','LoteC03'),(28,4.5,6.3,0,'2025-04-19 11:00:20','LoteC03'),(29,5,6.8,1,'2025-04-19 11:00:22','LoteC03'),(30,4.8,6.6,1,'2025-04-19 11:00:25','LoteC03');
/*!40000 ALTER TABLE `registro_piezas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-21 16:28:24
