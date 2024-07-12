-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 11, 2024 at 07:35 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pdf_converter`
--

-- --------------------------------------------------------

--
-- Table structure for table `pdf_files`
--

CREATE TABLE `pdf_files` (
  `id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `upload_time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pdf_files`
--

INSERT INTO `pdf_files` (`id`, `filename`, `file_path`, `upload_time`) VALUES
(23, 'cover sad.pdf', 'uploads\\cover sad.pdf', '2024-07-07 18:49:34'),
(24, 'ITAHARI NAMUNA COLLEGE (1).pdf', 'uploads\\ITAHARI NAMUNA COLLEGE (1).pdf', '2024-07-07 18:49:47'),
(25, 'cover sad.pdf', 'uploads\\cover sad.pdf', '2024-07-07 19:09:52'),
(26, 'SE.pdf', 'uploads\\SE.pdf', '2024-07-07 19:12:54'),
(27, 'ITAHARI NAMUNA COLLEGE.pdf', 'uploads\\ITAHARI NAMUNA COLLEGE.pdf', '2024-07-08 08:58:04'),
(28, 'SE.pdf', 'uploads\\SE.pdf', '2024-07-08 08:58:11');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `profile_pic` varchar(255) DEFAULT NULL,
  `points` int(11) DEFAULT 0,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `website` varchar(255) DEFAULT NULL,
  `github` varchar(255) DEFAULT NULL,
  `twitter` varchar(255) DEFAULT NULL,
  `instagram` varchar(255) DEFAULT NULL,
  `facebook` varchar(255) DEFAULT NULL,
  `job_title` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `address` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `created_at`, `profile_pic`, `points`, `updated_at`, `website`, `github`, `twitter`, `instagram`, `facebook`, `job_title`, `location`, `phone`, `mobile`, `address`) VALUES
(1, 'Daniel Travis', 'sijupinog@mailinator.com', 'scrypt:32768:8:1$xecTV2dcPR6nWAbh$cee847d5de9ec33a609cc629a235654ae783cc175653a6238ea1e31ec0bb9b1a247cfb25b35a9f1a6203448ca1a3ab6926aa2fef61171e6521e9e49cc71fd546', '2024-07-07 18:15:15', NULL, 0, '2024-07-10 16:58:57', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(3, '', 'wiqukib@mailinator.com', 'scrypt:32768:8:1$J2toaHieRAbAA22U$3189ccdd2dd5e1d9c53a5bcc22a894230a855dbfb611aa8d4a253d49730473a562cba4efb57f0ee22ade3bff6d656e885c15553defc6fdce82c673ef85e0787e', '2024-07-07 18:17:07', NULL, 0, '2024-07-11 05:32:15', 'https://bootswatch.com/litera/', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pdf_files`
--
ALTER TABLE `pdf_files`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pdf_files`
--
ALTER TABLE `pdf_files`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
