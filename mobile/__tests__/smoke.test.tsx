import { render } from "@testing-library/react-native";
import { Text } from "react-native";

test("renders a basic element", async () => {
  const { getByText } = await render(<Text>True Beef</Text>);
  expect(getByText("True Beef")).toBeTruthy();
});
