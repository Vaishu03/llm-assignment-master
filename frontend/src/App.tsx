import { useState } from "react";
// import "./App.css";

export default function App() {
  const [result, setResult] = useState();
  const [question, setQuestion] = useState();
  const [file, setFile] = useState();

  const handleQuestionChange = (event: any) => {
    setQuestion(event.target.value);
  };

  const handleFileChange = (event: any) => {
    setFile(event.target.files[0]);
    alert("File successfully uploaded!")
  };

  const handleSubmit = (event: any) => {
    event.preventDefault();

    const formData = new FormData();

    if (file) {
      formData.append("file", file);
    }
    if (question) {
      formData.append("question", question);
    }

    fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        setResult(data.result);
      })
      .catch((error) => {
        console.error("Error", error);
      });
  };

  return (
    <div className="appBlock">
      <form onSubmit={handleSubmit} className="form">
        <label htmlFor="question" className="text-sm font-medium leading-6 text-gray-900">
          Question:
        </label>
        <input
        className ="flex-1 ml-2 border-b-2 rounded-lg border-gray-300 bg-transparent py-2 px-1 text-black placeholder-gray-400 focus:outline-none focus:border-blue-500 sm:text-sm sm:leading-5"
        id="question"
        type="text"
        value={question}
        onChange={handleQuestionChange}
        placeholder="Ask your question here"
        />
        <br></br>
        <br></br>
        <label className="text-sm font-medium leading-6 text-gray-900" htmlFor="file">
          Upload file:
        </label>

        <input
  type="file"
  id="file"
  name="file"
  accept=".pdf, .docx, .txt, .csv"
  onChange={handleFileChange}
  className="hidden fileInput"
/>

<label htmlFor="file" className="cursor-pointer ml-2 bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded-md shadow-md transition duration-300 ease-in-out">
  Choose a file
</label>

        <br></br>
        <button
  className="submitBtn mt-10 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition duration-300 ease-in-out"
  type="submit"
  disabled={!file || !question}
>
  Submit
</button>

      </form>
      <br></br>
      <p className="resultOutput">Result: {result}</p>
    </div>
  );
}
