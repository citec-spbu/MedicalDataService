import Link from "next/link";

const Studynotfound = () => {
  return (
    <div className="h-screen w-screen flex justify-center items-center">
      Одно или более выбранных исследований недоступны в данный момент.
      Вернитесь к&nbsp;
      <Link href={"/browser"} className="text-blue-500">
        просмотру файлов
      </Link>
      &nbsp;и выберите другое исследование.
    </div>
  );
};

export default Studynotfound;
