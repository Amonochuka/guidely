import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav>
      <Link to="/">Search</Link>

      {" | "}

      <Link to="/admin">Admin</Link>
    </nav>
  );
}

export default Navbar;