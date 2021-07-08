<?php
$response = array();

if(isset($_POST['url']) && isset($_POST['platform'])){
    $url = $_POST['url'];
    $platform = $_POST['platform'];
    $script_to_run = 'C:\xampp\htdocs\shopmate_v1\python\scrape_detailedInfo.py';
    $result = shell_exec($script_to_run." "."\"" .$url."\""." ". $platform);

    if(!empty($result)){
        //echo json_encode(json_decode($result,true));
        echo $result;
    }

    else{
        $response['success']=FALSE;
        $response['message']="Failed to scrape data from the website.";
        echo json_encode($response);
    }
}

else{
    $response['success']=FALSE;
    $response['message']="Failed to scrape data from the website.";
    echo json_encode($response);
}
?>

