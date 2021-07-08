<?php
require_once 'include/db_functions.php';
$db = new DB_Functions();

// json response array
$response = array("error" => FALSE);
 
if (isset($_POST['uuid'])) {
 
    // receiving the post params
    $uuid = $_POST['uuid'];
 
    $result = $db->getUserNotificationsCount($uuid);
 
    if ($result != false) {
        $response["error"] = FALSE;
        $response["result"] = $result;
        echo json_encode($response);
    } else {
        $response["error"] = FALSE;
        $response["result"] = 0;
        echo json_encode($response);
    }

    // print_r($result);
} else {
    // required post params is missing
    $response["error"] = TRUE;
    $response["error_msg"] = "Required parameters are missing!";
    echo json_encode($response);
}
?>