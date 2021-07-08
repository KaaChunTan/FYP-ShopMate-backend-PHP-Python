<?php
require_once 'include/db_functions.php';
$db = new DB_Functions();

// json response array
$response = array("error" => FALSE);
 
if (isset($_POST['notification_id'])) {
 
    // receiving the post params
    $notification_id = $_POST['notification_id'];
 
    $result = $db->markNotificationAsRead($notification_id);
 
    if ($result != false) {
        $response["error"] = FALSE;
        $response["result"] = $result;
        echo json_encode($response);
    } else {
        $response["error"] = TRUE;
        $response["error_msg"] = "Unsuccessful mark notification as read. Please try again!";
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