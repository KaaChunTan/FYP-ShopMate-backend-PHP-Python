<?php
$response = array();

if(isset($_POST['item_id']) &&
    isset($_POST['shop_id'])&&
    isset($_POST['review_count'])&&
    isset($_POST['platform'])){

        $item_id = $_POST['item_id'];
        $shop_id = $_POST['shop_id'];
        $review_count = $_POST['review_count'];
        $platform = $_POST['platform'];

        $script_to_run = 'C:\xampp\htdocs\shopmate_v1\python\sentiment_analysis_predictions.py';
        $result = shell_exec($script_to_run." ".$item_id." ".$shop_id." ".$review_count." ".$platform);

        if(!empty($result)){
            echo $result;
        }

        else{
            $response['error']=FALSE;
            $response['message']="Unable to scrape data from the website.";
            echo json_encode($response);
        }
    }

else{
    $response['error']=FALSE;
    $response['message']="Unable to scrape data from the website.";
    echo json_encode($response);
}

?>