// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title LoanEventLogger - Ghi log các sự kiện quan trọng của khoản vay lên blockchain
contract LoanEventLogger {
    address public owner;

    enum LoanEventType {
        ApplicationSubmitted,
        ApplicationApproved,
        ApplicationRejected,
        LoanDisbursed,
        PaymentMade,
        LoanCompleted
    }

    event LoanEventLogged(
        address indexed student,
        uint256 loanId,
        LoanEventType eventType,
        string metadata,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only platform can log events");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function logLoanEvent(
        address student,
        uint256 loanId,
        LoanEventType eventType,
        string calldata metadata
    ) external onlyOwner {
        emit LoanEventLogged(student, loanId, eventType, metadata, block.timestamp);
    }

    function changeOwner(address newOwner) external onlyOwner {
        owner = newOwner;
    }
}
