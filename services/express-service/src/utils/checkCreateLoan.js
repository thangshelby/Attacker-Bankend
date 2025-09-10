export function checkUserValid(user) {
  if (!user) {
    return false;
  }
  if (user.kyc_status !== "Verified") return false;
  if (
    user.citizen_id === null ||
    user.citizen_id === undefined ||
    user.citizen_id === ""
  )
    return false;
  // if (
  //   user.citizen_card_front === null ||
  //   user.citizen_card_front === undefined ||
  //   user.citizen_card_front === ""
  // )
  //   return false;
  // if (
  //   user.citizen_card_back === null ||
  //   user.citizen_card_back === undefined ||
  //   user.citizen_card_back === ""
  // )
  //   return false;
  // if (
  //   user.address === null ||
  //   user.address === undefined ||
  //   user.address === ""
  // )
  //   return false;
  // if (user.phone === null || user.phone === undefined || user.phone === "")
  //   return false;
  // if (user.birth === null || user.birth === undefined || user.birth === "")
  //   return false;
  // if (user.gender === null || user.gender === undefined || user.gender === "")
  //   return false;
  if (user.email === null || user.email === undefined || user.email === "")
    return false;

  return true;
}

export function checkStudentValid(student) {
  if (!student) {
    return false;
  }
  if (
    student.student_id === null ||
    student.student_id === undefined ||
    student.student_id === ""
  ) {
    console.error("Student ID is missing");
    return false;
  }
  if (
    student.class_id === null ||
    student.class_id === undefined ||
    student.class_id === ""
  ) {
    console.error("Student class is missing");
    return false;
  }
  if (
    student.university === null ||
    student.university === undefined ||
    student.university === ""
  ) {
    console.error("Student university is missing");
    return false;
  }
  if (
    student.student_card_front === null ||
    student.student_card_front === undefined ||
    student.student_card_front === ""
  ) {
    console.error("Student card front is missing");
    return false;
  }
  if (
    student.student_card_back === null ||
    student.student_card_back === undefined ||
    student.student_card_back === ""
  ) {
    console.error("Student card back is missing");
    return false;
  }
  return true;
}

export function checkAcademicValid(academic) {
  if (!academic) {
    return false;
  }
  if (
    academic.gpa === null ||
    academic.gpa === undefined ||
    academic.gpa === ""
  ) {
    return false;
  }
  if (academic.transcripts.length === 0) {
    return false;
  }

  return true;
}
