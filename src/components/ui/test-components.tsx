// Test file to verify UI components work correctly
import { Button } from './button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './card';
import { Input } from './input';
import { Label } from './label';
import { Alert, AlertDescription } from './alert';

export const TestComponents = () => {
  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">UI Component Tests</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Card Component</CardTitle>
          <CardDescription>This is a card description</CardDescription>
        </CardHeader>
        <CardContent>
          <p>This is the card content</p>
        </CardContent>
      </Card>
      
      <div className="space-y-2">
        <Label htmlFor="test-input">Test Input</Label>
        <Input id="test-input" placeholder="Enter some text" />
      </div>
      
      <div className="space-x-2">
        <Button>Default Button</Button>
        <Button variant="secondary">Secondary Button</Button>
        <Button variant="destructive">Destructive Button</Button>
      </div>
      
      <Alert>
        <AlertDescription>This is a test alert</AlertDescription>
      </Alert>
      
      <Alert variant="destructive">
        <AlertDescription>This is a destructive alert</AlertDescription>
      </Alert>
    </div>
  );
};