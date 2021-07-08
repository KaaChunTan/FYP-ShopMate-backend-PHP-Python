<?php
// require_once 'include/db_functions.php';
// $db = new DB_Functions();

// $db->test();


$link = mysqli_connect("localhost","root","","shopmate");
if($link === false){
    die("ERROR: Could not connect. ". mysqli_connect_error());
}
// $sql = "INSERT INTO test(id) VALUES (200)";
// $link->query($sql);
$stmt = $link->prepare("INSERT INTO test(id) VALUES (200)");
$stmt->execute();

?>