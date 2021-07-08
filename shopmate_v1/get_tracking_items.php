<?php
require_once 'include/db_functions.php';
$db = new DB_Functions();

// json response array
$response = array("error" => FALSE);
 
if (isset($_POST['user_id'])) {
 
    // receiving the post params
    $user_id = $_POST['user_id'];
 
    $result = $db->getTrackingItem($user_id);
 
    if ($result != false) {
        $response["error"] = FALSE;
        $response["result"] = $result;
        echo json_encode($response);
    } else {
        $response["error"] = TRUE;
        $response["error_msg"] = "Unsuccessful retrieving tracking items. Please try again!";
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