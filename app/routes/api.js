var express = require('express');
var router = express.Router();

var Web3 = require("web3");
var voteArtifacts = require("../../vote/contracts/Vote.sol");

var adminAddress = "";
var votersAddress = []

web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));

var voteContract = web3.eth.Contract(voteArtifacts.abi);
var deployedContract = null
voteContract.transactionConfirmationBlocks = 1;

const privateKey = "-----BEGIN RSA PRIVATE KEY-----\nMIICWwIBAAKBgQC5M5llDEzIyEWi4eUdxQqnY6DaPE63TQo/NbUZ+JaMBZLGJyjy\nu7uQbv3tk3o8OmuVbBSDLlBgJVuuFRnucdH4P+oyn9SU8F05M2jNNEc4CZiLepBp\nrgHV7MJLh5xU/2TjuPQOdQEHDIrUajZsXLWtxwh6hiqV1nzsW9IV1FwjCQIDAQAB\nAoGAHCm6k+Ew8/9wh3puiv5hxl6iIU22cq1md4JFTfO9gQF/9l4SHgdqWGZoeu5I\nUkxX+9r5q5Epa9WCgZB35wir8yAbNnez8uOWhAt9sAi1u4lUsoLlmjbX+3WtZM/Y\nO74DF0qzE5vT4/wXm7Njp2NXB/F7X2nPzxaPqYMIAMxE6ZkCQQDbj59hJp237SdK\n6G6R0iPlxpAlGY0MijrRzcAlz/U5OzYYTHrhLLU7IcF5Oxt+ZpCIFEhFWkfCy5VB\nWtHRyASvAkEA1/Ap2hPGbSnZpxu9J16fIenS3Gwy4JoE5P1rclBq6oPBg9LtxKXu\n3u60cAw/46QoYYvvIJ8q7VkToXCKO3UxxwJAPUZd4o0WYyhKWPt5MDUHU68Qt2nk\nFWXWeIsFXwgkle5ScIGXoZQKmBAZoK3ARIx3NaMDcGd7s3+BjhW8jOFXfQJADCKY\nB4Ri+1GFxMlfSO4dXUeJrQ97kHm3WrMPLb5tM76xylm5OPrmQKsDguR9VqqsBkdZ\n6ehn/iyqWME9U3gTkwJAdR0TRN1UtYp/LrT4TG2RPbeyS3HKBVLN4flyVUvNsTbQ\nLD2ErBiLhcG9EaXT2rwiU5j2xcFckhNLaVuif0Je9Q==\n-----END RSA PRIVATE KEY-----"
const publicKey = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC5M5llDEzIyEWi4eUdxQqnY6Da\nPE63TQo/NbUZ+JaMBZLGJyjyu7uQbv3tk3o8OmuVbBSDLlBgJVuuFRnucdH4P+oy\nn9SU8F05M2jNNEc4CZiLepBprgHV7MJLh5xU/2TjuPQOdQEHDIrUajZsXLWtxwh6\nhiqV1nzsW9IV1FwjCQIDAQAB\n-----END PUBLIC KEY-----"


// web3.eth.personal.unlockAccount("0x535ab32b34a3bf68d17df9452511245bb5f37d33", "", 0);

web3.eth.personal.getAccounts().then((accounts) => {
  adminAddress = accounts[0];
  votersAddress = accounts.splice(1);

  const deploy = async () => {
    const gas = await voteContract.deploy({
      data: voteArtifacts.bytecode
    }).estimateGas();
    const response = await voteContract.deploy({
      data: voteArtifacts.bytecode
    }).send({
      from: adminAddress,
      gas: gas + 1
    });
    console.log('Contract deployed to:', response.address);
    return response
  };
  deploy().then((contractClone) => {
    deployedContract = contractClone
  });
})

/* GET Request */
router.get('/vote', function (req, res) {
  deployedContract.methods.getOptions().call({ from: adminAddress }).then((optionResult) => {
    deployedContract.methods.getDeadline().call({ from: adminAddress }).then((deadlineResult) => {
      let deadline = new Date(deadlineResult * 1000);
      res.send({
        options: optionResult,
        deadline: deadline
      })
    }).catch((deadlineErr) => {
      console.log(deadlineErr)
      res.status(400)
      res.send("Voting is Closed!")
    })
  }).catch((optionErr) => {
    console.log(optionErr)
    res.status(400)
    res.send("Error!")
  })
});

router.get('/state', function(req,res){
  deployedContract.methods.getState().call({from: adminAddress}).then((result) => {
    res.send({
      state: result
    })
  })
})

router.get('/ticket', function(req, res){ 
  deployedContract.methods.getTickets().call({ from: adminAddress }).then((result) => {
    res.send({
      tickets: result
    })
  }).catch((err) => {
    console.log(err)
    res.status(400)
    res.send("Voteing is Not Closed!")
  })
})

router.get('/option', function(req, res){
  deployedContract.methods.getOptions().call({from: adminAddress}).then((result) => {
    res.send({
      options: result
    })
  })
})

router.get('/address', function(req, res){
  res.send({
    admin: adminAddress,
    voter: votersAddress
  })
})

router.get('/key', function(req, res){
  res.send({
    publicKey: publicKey,
    privateKey: privateKey
  })
})


/* POST Request */
router.post('/vote', function (req, res) {
  let params = req.body.params;
  let deadline = new Date(params.deadline).getTime() / 1000
  console.log("deadline is : " + deadline)
  if (deadline < 0)
    deadline = 1

  deployedContract.methods.createVote(params.options, deadline, adminAddress).send({
    from: adminAddress,
    gas: 6000000,
    gasPrice: "1"
  }, (err, transactionHash) => {
    if (err) {
      console.log("Create Vote Error!: " + err)
      res.status(400)
      res.send("Vote is already Created!")
    } else {
      console.log("Txid: " + transactionHash);
      for(let i = 0; i < votersAddress.length; i++){
        deployedContract.methods.registerVoter(votersAddress[i]).send({
          from: adminAddress,
          gas: 6000000,
          gasPrice: "1"
        }, (err, transactionHash) => {
          if(err){
            console.log(err)
          } else{
            console.log(transactionHash)
          }
        })
      }
      res.send("Vote Created!")
    }
  })
});

router.post('/ticket', function (req, res) {
  let params = req.body.params;
  deployedContract.methods.vote(params.ticket).send({
    from: votersAddress[params.index],
    gas: 6000000,
    gasPrice: "1"
  }, (err, transactionHash) => {
    if(err){
      console.log(err)
      res.status(400)
      res.send("Vote Fail!")
    } else {
      console.log("Txid: " + transactionHash)
      res.send("Vote done!")
    }
  })
})

/* Put Request */
router.put('/vote', function (req, res) {
  let state = req.body.params.state;

  switch(state){
    case "PROCEEDING":{
      deployedContract.methods.openVoting().send({
        from: adminAddress,
        gas: 6000000,
        gasPrice: "1"
      }, (err, transactionHash) => {
        if(err){
          console.log(err)
          res.status(400)
          res.send("Vote is Not Pending!")
        } else{
          console.log("TxID: " + transactionHash);
          res.send("Vote is Open!")
        }
      })
      break;
    }
    case "CLOSED":{
      deployedContract.methods.closeVoting(privateKey).send({
        from: adminAddress,
        gas: 6000000,
        gasPrice: "1"
      }, (err, transactionHash) => {
        if(err){
          console.log(err)
          res.status(400)
          res.send("Vote can not be Closed!")
        } else{
          console.log("TxID: " + transactionHash);
          res.send("Vote is Closed!")
        }
      })
      break;
    }
    default:{
      res.sendStatus(400)
    }
  }
});

module.exports = router;